# Time Sequence Filtering User Guide

## Overview

The Time Sequence filtering feature provides advanced log analysis capabilities with intelligent message type categorization, OR logic filtering, and efficient pagination. This guide explains how to use these features effectively.

## Features

### 🎯 Message Type Categorization

The system automatically categorizes log messages into meaningful types based on content patterns:

#### wnc-steer Application Categories
- **Client Management**: Client connection and management events
- **General Information**: General system information and status
- **Network Operations**: Network connectivity and operation events
- **Configuration**: System configuration and settings
- **Steering Decisions**: Client steering decision events
- **Steering Actions**: Executed steering actions
- **Steering Evaluation**: Steering effectiveness evaluation

#### wnc-acs Application Categories
- **Channel Selection**: Auto channel selection events
- **Network Analysis**: Network analysis and optimization
- **Configuration**: ACS configuration and settings
- **Performance**: Performance monitoring and metrics

#### otbr-agent Application Categories
- **Thread Management**: OpenThread network management
- **Border Router**: Border router operations
- **Matter Integration**: Matter IoT protocol events
- **Network Topology**: Network topology management

### 🔍 OR Logic Filtering

The system supports filtering by multiple message types simultaneously using OR logic:

- **Single Filter**: Select one message type to show only those events
- **Multiple Filters**: Select multiple message types to show events matching ANY of the selected types
- **Dynamic Counts**: Filter counts update automatically based on available data

### 📄 Pagination

Efficient pagination with 25 items per page:

- **Page Navigation**: Navigate through results using pagination controls
- **Total Count**: See total number of matching events across all pages
- **Current Page**: Display current page number and total pages
- **Quick Access**: Jump to specific pages or navigate sequentially

## How to Use

### 1. Accessing Time Sequence View

1. **Navigate to Project**: Select a project from the dashboard
2. **Choose Application**: Click on an application (e.g., wnc-steer)
3. **Open Analysis**: Click on the analysis result
4. **Time Sequence Tab**: Click on the "Time Sequence" tab

### 2. Applying Filters

#### Single Message Type Filter
1. **Open Filter Panel**: Click the filter icon or expand the filter panel
2. **Select Filter**: Check the box next to a message type (e.g., "Configuration")
3. **Apply Filter**: Click "Apply Filters" button
4. **View Results**: See only configuration-related events

#### Multiple Message Type Filters (OR Logic)
1. **Select Multiple Filters**: Check multiple message type boxes
   - Example: Select "Configuration" AND "Steering Decisions"
2. **Apply Filters**: Click "Apply Filters" button
3. **View Combined Results**: See events that match EITHER configuration OR steering decisions

#### Clear All Filters
1. **Deselect All**: Uncheck all message type boxes
2. **Apply Filters**: Click "Apply Filters" button
3. **View All Events**: See all events without filtering

### 3. Navigating Results

#### Pagination Controls
- **Page Numbers**: Click on page numbers to jump to specific pages
- **Previous/Next**: Use arrow buttons to navigate sequentially
- **Page Info**: View "X events on page Y of Z (Total events)" information

#### Event Details
- **Event List**: Scroll through events on the current page
- **Event Selection**: Click on an event to see detailed information
- **Event Metadata**: View timestamp, severity, message type, and container information

### 4. Understanding the Display

#### Event Information
Each event displays:
- **Timestamp**: When the event occurred
- **Event Type**: The categorized message type
- **Severity**: Log level (INFO, WARN, ERROR, etc.)
- **Message**: Truncated log message (first 100 characters)
- **Category Badge**: Visual indicator of the message type

#### Filter Panel
- **Filter List**: All available message types with counts
- **Count Display**: Number of events for each message type
- **Color Coding**: Each filter has a unique color for easy identification
- **Apply Button**: Apply selected filters to the timeline

## Best Practices

### 1. Filter Selection Strategy

#### Start Broad, Then Narrow
1. **Initial View**: Start with all events to understand the data
2. **Identify Patterns**: Look for interesting patterns or anomalies
3. **Apply Specific Filters**: Use specific message types to focus on relevant events
4. **Combine Filters**: Use OR logic to analyze related event types together

#### Common Filter Combinations
- **Configuration + Steering Decisions**: Analyze system configuration impact on steering
- **Network Operations + General Info**: Monitor network health and general status
- **Steering Actions + Steering Evaluation**: Track steering effectiveness

### 2. Pagination Strategy

#### Efficient Navigation
- **Use Page Numbers**: Jump directly to specific pages for faster navigation
- **Monitor Total Count**: Pay attention to total event counts to understand data volume
- **Page Size**: 25 events per page provides good balance of detail and performance

#### Data Analysis
- **First Page**: Often contains the most recent or important events
- **Last Page**: May contain older events or less critical information
- **Middle Pages**: Useful for finding specific time periods or patterns

### 3. Performance Tips

#### Filter Optimization
- **Start with Fewer Filters**: Begin with 1-2 filters, then add more as needed
- **Use Specific Filters**: More specific filters return fewer, more relevant results
- **Clear Unused Filters**: Remove filters you're not actively using

#### Navigation Efficiency
- **Use Pagination**: Don't try to load all events at once
- **Focus on Relevant Pages**: Navigate to pages containing events of interest
- **Use Event Selection**: Click on events to see full details without loading more data

## Troubleshooting

### Common Issues

#### No Events Displayed
1. **Check Filters**: Ensure filters are not too restrictive
2. **Clear Filters**: Try clearing all filters to see all events
3. **Check Data**: Verify that the application has log data
4. **Refresh Page**: Try refreshing the browser page

#### Slow Performance
1. **Reduce Filters**: Use fewer filters to reduce data processing
2. **Check Network**: Ensure stable network connection
3. **Browser Performance**: Close unnecessary browser tabs
4. **Data Size**: Large datasets may take longer to process

#### Missing Message Types
1. **Data Processing**: Ensure log data has been processed and categorized
2. **Application Support**: Verify the application supports message type categorization
3. **Database Status**: Check that SQLite databases are properly initialized

### Getting Help

#### Debug Information
- **Browser Console**: Check browser developer console for errors
- **Network Tab**: Monitor API requests in browser developer tools
- **Backend Logs**: Check backend logs for processing errors

#### Support
- **Documentation**: Refer to system documentation for technical details
- **API Endpoints**: Use API documentation to understand data structure
- **Log Files**: Check application log files for detailed error information

## Advanced Usage

### API Integration

#### Direct API Access
```bash
# Get filtered logs with OR logic
curl "http://localhost:8000/api/v1/projects/{project_id}/applications/{app_name}/data/logs?message_types=configuration,steering_decision&limit=25&offset=0"

# Get message types and counts
curl "http://localhost:8000/api/v1/projects/{project_id}/applications/{app_name}/data/message-types"
```

#### Custom Filtering
- **Time Range**: Add `start_time` and `end_time` parameters
- **Log Level**: Filter by specific log levels (INFO, WARN, ERROR)
- **Container ID**: Filter by specific container instances
- **Text Search**: Use `query` parameter for full-text search

### Data Export

#### CSV Export
```bash
# Export filtered data to CSV
curl "http://localhost:8000/api/v1/projects/{project_id}/applications/{app_name}/data/export/csv?message_types=configuration,steering_decision"
```

#### Custom Analysis
- **Statistical Analysis**: Use analytics endpoints for advanced statistics
- **Correlation Analysis**: Analyze correlations between different message types
- **Performance Metrics**: Get performance metrics and trend analysis

## Conclusion

The Time Sequence filtering feature provides powerful tools for analyzing log data with intelligent categorization, flexible filtering, and efficient navigation. By understanding the message types, using OR logic effectively, and leveraging pagination, users can efficiently analyze large volumes of log data to gain insights into system behavior and performance.

For technical details and API documentation, refer to the system specification and API documentation.
