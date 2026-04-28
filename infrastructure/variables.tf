variable "resource_group_name" {
  description = "The name of the resource group"
  type        = string
  default     = "rg-dbe-ai-expert-system"
}

variable "location" {
  description = "The Azure location for resources"
  type        = string
  default     = "East US"
}

variable "environment" {
  description = "The deployment environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}
