import re

import pulumi
from pulumi import Output, export, get_project
import pulumi_azure as azure

LOCATION = "francecentral"
PROJECT = get_project()


def stack_name(suffix: str) -> str:
    return f"{PROJECT}-{suffix}"


def sanitize_registry_name(raw: str) -> str:
    clean = re.sub("[^a-z0-9]", "", raw.lower())
    if not 5 <= len(clean) <= 50:
        raise ValueError("Registry name must be 5-50 lowercase alphanumeric characters.")
    return clean


REGISTRY_NAME = sanitize_registry_name(PROJECT)
REGISTRY_LOGIN = f"{REGISTRY_NAME}.azurecr.io"
REGISTRY_URL = f"https://{REGISTRY_LOGIN}"
DOCKER_IMAGE_NAME = f"{PROJECT}:latest"

# Configure provider to allow deleting non-empty resource groups.
azure_provider = azure.Provider(
    "azure-provider",
    features=azure.ProviderFeaturesArgs(
        resource_group=azure.ProviderFeaturesResourceGroupArgs(
            prevent_deletion_if_contains_resources=False,
        )
    ),
)
default_opts = pulumi.ResourceOptions(provider=azure_provider)

# Resource Group
resource_group = azure.core.ResourceGroup(
    "resource_group",
    name=PROJECT,
    location=LOCATION,
    opts=default_opts,
)

# App Service Plan for Linux workloads
service_plan = azure.appservice.ServicePlan(
    "service_plan",
    name=stack_name("plan"),
    location=resource_group.location,
    resource_group_name=resource_group.name,
    os_type="Linux",
    sku_name="B1",
    opts=default_opts,
)

# Azure Container Registry
registry = azure.containerservice.Registry(
    "registry",
    name=REGISTRY_NAME,
    resource_group_name=resource_group.name,
    location=resource_group.location,
    sku="Basic",
    admin_enabled=True,
    opts=default_opts,
)

# Log Analytics Workspace (operational insights workspace)
workspace = azure.operationalinsights.AnalyticsWorkspace(
    "workspace",
    name=stack_name("log"),
    resource_group_name=resource_group.name,
    location=resource_group.location,
    sku="PerGB2018",
    retention_in_days=30,
    opts=default_opts,
)

# Application Insights resource connected to the workspace
app_insights = azure.appinsights.Insights(
    "app_insights",
    name=stack_name("insights"),
    resource_group_name=resource_group.name,
    location=resource_group.location,
    application_type="web",
    sampling_percentage=0,
    workspace_id=workspace.id,
    opts=default_opts,
)

# Registry credentials are used to build the web app settings.
registry_info = azure.containerservice.get_registry_output(
    name=registry.name,
    resource_group_name=resource_group.name,
)
registry_username = registry_info.admin_username
registry_password = registry_info.admin_password

# Linux Web App backed by the App Service Plan.
web_app = azure.appservice.LinuxWebApp(
    "web_app",
    name=stack_name("app"),
    resource_group_name=resource_group.name,
    location=resource_group.location,
    service_plan_id=service_plan.id,
    site_config=azure.appservice.LinuxWebAppSiteConfigArgs(
        always_on=True,
        application_stack=azure.appservice.LinuxWebAppSiteConfigApplicationStackArgs(
            docker_image_name=DOCKER_IMAGE_NAME,
            docker_registry_url=REGISTRY_URL,
            docker_registry_username=registry_username,
            docker_registry_password=registry_password,
        ),
    ),
    app_settings={
        "WEBSITES_ENABLE_APP_SERVICE_STORAGE": "true",
        "WEBSITES_PORT": "8000",
        "APPINSIGHTS_INSTRUMENTATIONKEY": app_insights.instrumentation_key,
        "APPLICATIONINSIGHTS_CONNECTION_STRING": app_insights.connection_string,
    },
    opts=default_opts,
)

# Monitor alert equivalent to the Terraform azurerm_monitor_scheduled_query_rules_alert_v2 resource.
alert = azure.monitoring.ScheduledQueryRulesAlertV2(
    "negative_feedback_alert",
    name="negative-feedback",
    location=resource_group.location,
    resource_group_name=resource_group.name,
    enabled=True,
    evaluation_frequency="PT5M",
    window_duration="PT5M",
    scopes=app_insights.id,
    severity=3,
    target_resource_types=["microsoft.insights/components"],
    criterias=[
        azure.monitoring.ScheduledQueryRulesAlertV2CriteriaArgs(
            query='customEvents\n| where customDimensions.correct == "False"\n',
            time_aggregation_method="Count",
            operator="GreaterThan",
            threshold=3,
            failing_periods=azure.monitoring.ScheduledQueryRulesAlertV2CriteriaFailingPeriodsArgs(
                minimum_failing_periods_to_trigger_alert=1,
                number_of_evaluation_periods=1,
            ),
        )
    ],
    description="Alert when negative feedback traces exceed threshold.",
    display_name="negative feedback",
    opts=default_opts,
)

export("app_service_url", web_app.default_hostname)
export("log_analytics_workspace_id", workspace.id)
export("docker_registry_password", Output.secret(registry_password))
export("application_insights_id", app_insights.id)
