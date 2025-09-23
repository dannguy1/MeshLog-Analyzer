# prplOS LCM Log Analysis System - Frontend

A modern React.js frontend for the prplOS LCM Log Analysis System, built with TypeScript, Material-UI, and Redux Toolkit.

## Features

- **Modern React Architecture**: Built with React 18, TypeScript, and functional components with hooks
- **Material-UI Design**: Beautiful, responsive UI using Material-UI v5 components
- **State Management**: Redux Toolkit for predictable state management
- **Real-time Updates**: WebSocket integration for live monitoring and alerts
- **Responsive Design**: Mobile-first design that works on all devices
- **Type Safety**: Full TypeScript support for better development experience

## Pages

### Dashboard
- Overview of projects and analyses
- Quick statistics and metrics
- Recent activity feed
- Quick action buttons

### Project Upload
- Drag-and-drop file upload
- Support for .tar, .tar.gz, .tgz, and .zip files
- Project metadata management
- Upload progress tracking

### Analysis View
- Detailed analysis results
- Progress tracking for running analyses
- Interactive charts and visualizations
- Recommendations and insights

### Real-time Monitor
- Live monitoring dashboard
- WebSocket-based real-time updates
- Alert management and acknowledgment
- Configurable thresholds and settings

## Technology Stack

- **React 18**: Modern React with concurrent features
- **TypeScript**: Type-safe JavaScript development
- **Material-UI v5**: Component library and theming
- **Redux Toolkit**: State management
- **React Router v6**: Client-side routing
- **React Query**: Server state management
- **Vite**: Fast build tool and dev server
- **Axios**: HTTP client for API communication
- **WebSocket**: Real-time communication
- **Chart.js**: Chart visualization library
- **D3.js**: Advanced data visualization

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm 8+

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser to `http://localhost:3000`

### Development

- **Development server**: `npm run dev`
- **Build for production**: `npm run build`
- **Preview production build**: `npm run preview`
- **Type checking**: `npm run type-check`
- **Linting**: `npm run lint`
- **Formatting**: `npm run format`
- **Testing**: `npm run test`

## Project Structure

```
src/
├── components/          # Reusable UI components
│   └── Layout.tsx      # Main layout component
├── pages/              # Page components
│   ├── Dashboard.tsx
│   ├── ProjectUpload.tsx
│   ├── AnalysisView.tsx
│   ├── RealTimeMonitor.tsx
│   └── NotFound.tsx
├── store/              # Redux store configuration
│   ├── index.ts
│   └── features/       # Redux slices
│       ├── projects/
│       ├── analysis/
│       ├── visualization/
│       └── alerts/
├── services/           # API and external services
│   └── api.ts
├── utils/              # Utility functions
├── types/              # TypeScript type definitions
├── App.tsx             # Main app component
└── main.tsx           # Application entry point
```

## API Integration

The frontend communicates with the backend through REST APIs and WebSocket connections:

- **REST API**: HTTP endpoints for CRUD operations
- **WebSocket**: Real-time updates for monitoring and alerts
- **File Upload**: Multipart form data for project uploads

## State Management

Redux Toolkit is used for state management with the following slices:

- **Projects**: Project management and file uploads
- **Analysis**: Analysis results and progress tracking
- **Visualization**: Charts, dashboards, and monitoring
- **Alerts**: Real-time alerts and notifications

## Theming

Material-UI theming is configured with:

- Custom color palette
- Typography settings
- Component overrides
- Responsive breakpoints

## Testing

The application includes comprehensive testing:

- **Unit tests**: Component and utility testing
- **Integration tests**: Redux store and API integration
- **E2E tests**: End-to-end user workflows

## Build and Deployment

### Production Build

```bash
npm run build
```

This creates optimized production files in the `dist/` directory.

### Development Build

```bash
npm run dev
```

This starts a development server with hot reloading.

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
```

### API Configuration

The API base URL and endpoints are configured in `src/services/api.ts`.

## Contributing

1. Follow the existing code style and patterns
2. Write tests for new features
3. Update documentation as needed
4. Use TypeScript for all new code

## License

This project is part of the prplOS LCM Log Analysis System.
