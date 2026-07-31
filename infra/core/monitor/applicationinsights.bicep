metadata description = 'Creates an Application Insights instance based on an existing Log Analytics workspace.'
param name string
param dashboardName string = ''
param location string = resourceGroup().location
param tags object = {}
param logAnalyticsWorkspaceId string

@description('Optional. Principal ID of the Foundry Project managed identity to grant Log Analytics Reader.')
param projectMIPrincipalId string = ''

@description('Optional. Principal ID of the developer/user to grant Monitoring Reader on Application Insights (for the Observe skill — viewing traces).')
param userPrincipalId string = ''

@description('Optional. Principal type of userPrincipalId (User or ServicePrincipal).')
param userPrincipalType string = 'User'

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: name
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspaceId
  }
}

module applicationInsightsDashboard 'applicationinsights-dashboard.bicep' = if (!empty(dashboardName)) {
  name: 'application-insights-dashboard'
  params: {
    name: dashboardName
    location: location
    applicationInsightsName: applicationInsights.name
  }
}

// Reference the linked Log Analytics workspace to scope the role assignment correctly.
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' existing = {
  name: last(split(logAnalyticsWorkspaceId, '/'))
}

// Log Analytics Data Reader for the Foundry Project managed identity, scoped to the Log Analytics workspace.
// Per https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/hosted-agent-permissions:
//   "Log Analytics Data Reader is the recommended built-in role" for the project MI on the workspace.
// Required for the evaluations feature to read agent trace data from the workspace.
// Note: this differs from Log Analytics Reader (73c42c96) — the Data Reader role (3b03c2da) is the
//   specific built-in that the Foundry evaluations service checks for workspace read access.
resource logAnalyticsDataReaderRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(projectMIPrincipalId)) {
  scope: logAnalyticsWorkspace
  name: guid(logAnalyticsWorkspaceId, projectMIPrincipalId, '3b03c2da-16b3-4a49-8834-0f8130efdd3b')
  properties: {
    principalId: projectMIPrincipalId
    principalType: 'ServicePrincipal'
    // Log Analytics Data Reader: 3b03c2da-16b3-4a49-8834-0f8130efdd3b
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '3b03c2da-16b3-4a49-8834-0f8130efdd3b')
  }
}

// Monitoring Reader for the developer, scoped to the Application Insights resource.
// Per https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/hosted-agent-permissions#viewing-telemetry-data:
//   "Assign Monitoring Reader at the Application Insights resource scope. The */read permissions in
//    this role access the underlying Log Analytics workspace data without requiring a separate
//    workspace-scoped assignment."
// Required for the Observe skill (viewing agent traces). Foundry User alone is insufficient —
// it sees metrics but NOT traces.
// Monitoring Reader: 43d0d8ad-25c7-4714-9337-8ba259a9fe05
resource userMonitoringReaderRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(userPrincipalId)) {
  scope: applicationInsights
  name: guid(applicationInsights.id, userPrincipalId, '43d0d8ad-25c7-4714-9337-8ba259a9fe05')
  properties: {
    principalId: userPrincipalId
    principalType: userPrincipalType
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '43d0d8ad-25c7-4714-9337-8ba259a9fe05')
  }
}

output connectionString string = applicationInsights.properties.ConnectionString
output id string = applicationInsights.id
output instrumentationKey string = applicationInsights.properties.InstrumentationKey
output name string = applicationInsights.name
