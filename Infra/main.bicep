param location string = resourceGroup().location
param sqlUser string
param sqlPassword string

resource sql 'Microsoft.Sql/servers@2021-11-01-preview' = {
  name: 'store-sql'
  location: location
  properties: {
    administratorLogin: sqlUser
    administratorLoginPassword: sqlPassword
  }
}

resource sqlDB 'Microsoft.Sql/servers/databases@2021-11-01-preview' = {
  name: '${sql.name}/storedb'
  location: location
}

resource storage 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: 'storestorage'
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
}

resource insights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'store-insights'
  location: location
  properties: { Application_Type: 'web' }
}
