output "kube_config" {
  value = azurerm_kubernetes_cluster.main.kube_config_raw
  sensitive = true
}

output "storage_account_name" {
  value = azurerm_storage_account.main.name
}

output "container_name" {
  value = azurerm_storage_container.main.name
}
