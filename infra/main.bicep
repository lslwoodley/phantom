@description('Azure region for deployment')
param location string = resourceGroup().location

@description('Existing Container Apps environment name, if reusing')
param existingContainerAppsEnvName string = 'agent-ca-env'

@description('Existing Application Insights name, if reusing')
param existingAppInsightsName string = 'appi-e7gh5iceqsisa'

@description('Container registry name (existing)')
param existingContainerRegistryName string = 'cre7gh5iceqsisa'

var backendContainerImage = '${existingContainerRegistryName}.azurecr.io/phantom-backend:latest'
var frontendContainerImage = '${existingContainerRegistryName}.azurecr.io/phantom-frontend:latest'

var backendAppName = 'phantom-backend'
var frontendAppName = 'phantom-frontend'

@description('Reuse existing resources if true; create new otherwise')
param reuseExistingResources bool = true

// Conditional resource definitions for existing or new Container Apps Environment
resource containerAppsEnv 'Microsoft.App/managedEnvironments@2022-03-01' = if (!reuseExistingResources) {
  name: existingContainerAppsEnvName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsWorkspace.properties.customerId
        sharedKey: logAnalyticsWorkspace.listKeys().primarySharedKey
      }
    }
  }
}

// Reference existing Container Apps Environment (if reusing)
resource existingEnv 'Microsoft.App/managedEnvironments@2022-03-01' existing = if (reuseExistingResources) {
  name: existingContainerAppsEnvName
}

// Conditional Application Insights definition (existing/new)
resource appInsights 'Microsoft.Insights/components@2020-02-02' = if (!reuseExistingResources) {
  name: existingAppInsightsName
  location: location
  properties: {
    Application_Type: 'web'
  }
}

// Reference existing Application Insights (if reusing)
resource existingAppInsights 'Microsoft.Insights/components@2020-02-02' existing = if (reuseExistingResources) {
  name: existingAppInsightsName
}

// Reference existing Container Registry
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2021-12-01-preview' existing = {
  name: existingContainerRegistryName
}

// Backend Container App
resource backendContainerApp 'Microsoft.App/containerApps@2022-03-01' = {
  name: backendAppName
  location: location
  properties: {
    managedEnvironmentId: reuseExistingResources ? existingEnv.id : containerAppsEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
      }
      secrets: [
        {
          name: 'openai-api-key'
          value: '${OPENAI_API_KEY}'
        }
      ]
      environmentVariables: [
        { name: 'OPENAI_MODEL', value: '${OPENAI_MODEL}' }
        { name: 'OPENAI_EMBEDDING_DEPLOYMENT', value: '${OPENAI_EMBEDDING_DEPLOYMENT}' }
        { name: 'OPENAI_ENDPOINT', value: '${OPENAI_ENDPOINT}' }
        { name: 'PHANTOM_TENANT_ID', value: '${PHANTOM_TENANT_ID}' }
        { name: 'PHANTOM_APP_CLIENT_ID', value: '${PHANTOM_APP_CLIENT_ID}' }
        { name: 'PHANTOM_APP_SECRET', value: '${PHANTOM_APP_SECRET}' }
      ]
    }
    template: {
      containers: [
        {
          name: backendAppName
          image: backendContainerImage
          env: [
            {
              name: 'OPENAI_API_KEY'
              secretRef: 'openai-api-key'
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
}

// Frontend Container App
resource frontendContainerApp 'Microsoft.App/containerApps@2022-03-01' = {
  name: frontendAppName
  location: location
  properties: {
    managedEnvironmentId: reuseExistingResources ? existingEnv.id : containerAppsEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 3000
      }
    }
    template: {
      containers: [
        {
          name: frontendAppName
          image: frontendContainerImage
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 2
      }
    }
  }
}

// Optional: Log Analytics Workspace (if creating new resources)
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2021-12-01-preview' = if (!reuseExistingResources) {
  name: 'log-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    retentionInDays: 30
  }
}

// Outputs
output backendContainerAppURL string = backendContainerApp.properties.configuration.ingress.fqdn
output frontendContainerAppURL string = frontendContainerApp.properties.configuration.ingress.fqdn
