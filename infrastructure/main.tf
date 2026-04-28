terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_user_assigned_identity" "expert_system_identity" {
  name                = "id-dbe-expert-system-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
}

resource "azurerm_key_vault" "main" {
  name                        = "kv-dbe-${var.environment}"
  location                    = azurerm_resource_group.main.location
  resource_group_name         = azurerm_resource_group.main.name
  enabled_for_disk_encryption = true
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days  = 7
  purge_protection_enabled    = false

  sku_name = "standard"

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    key_permissions = ["Get", "List", "Create"]
    secret_permissions = ["Get", "List", "Set"]
  }
}

data "azurerm_client_config" "current" {}

resource "azurerm_cosmosdb_account" "main" {
  name                = "cosmos-dbe-expert-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB" # Gremlin is enabled via capabilities

  enable_automatic_failover = false

  capabilities {
    name = "EnableGremlin"
  }

  consistency_policy {
    consistency_level = "Session"
  }

  geo_location {
    location          = azurerm_resource_group.main.location
    failover_priority = 0
  }
}

resource "azurerm_application_insights" "main" {
  name                = "appi-dbe-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  application_type    = "web"
}

resource "azurerm_machine_learning_workspace" "main" {
  name                    = "mlw-dbe-${var.environment}"
  location                = azurerm_resource_group.main.location
  resource_group_name     = azurerm_resource_group.main.name
  application_insights_id = azurerm_application_insights.main.id
  key_vault_id            = azurerm_key_vault.main.id
  storage_account_id      = azurerm_storage_account.ml_storage.id

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_storage_account" "ml_storage" {
  name                     = "stdbeexpert${var.environment}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_kubernetes_cluster" "main" {
  name                = "aks-dbe-expert-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = "dbe-expert"

  default_node_pool {
    name       = "default"
    node_count = 2
    vm_size    = "Standard_DS2_v2"
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin    = "azure"
    load_balancer_sku = "standard"
  }
}

resource "azurerm_api_management" "main" {
  name                = "apim-dbe-expert-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  publisher_name      = "DBE Expert System"
  publisher_email     = "admin@dbe.gov"

  sku_name = "Developer_1"
}

resource "azurerm_monitor_action_group" "main" {
  name                = "ag-dbe-expert-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  short_name          = "DBEAlerts"

  email_receiver {
    name          = "sendtoadmin"
    email_address = "admin@dbe.gov"
  }
}

resource "azurerm_portal_dashboard" "main" {
  name                = "dashboard-dbe-expert-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  dashboard_properties = jsonencode({
    lenses = {
      "0" = {
        order = 0
        parts = []
      }
    }
    metadata = {
      model = {
        timeRange = {
          value = {
            relative = {
              duration = 24
              timeUnit = 1
            }
          }
          type = "MsPortalFx.Composition.Configuration.ValueTypes.TimeRange"
        }
      }
    }
  })
}
