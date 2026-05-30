# System Architecture

## Data Flow Diagram

```mermaid
graph TB
    subgraph "Data Sources"
        A[Wikipedia Squad Pages]
        B[Transfermarkt Player Pages]
    end
    
    subgraph "Data Collection Layer"
        C[Wikipedia Scraper]
        D[Transfermarkt Scraper]
    end
    
    subgraph "Raw Data Storage"
        E[Raw Rosters CSV]
        F[Raw Market Values CSV]
    end
    
    subgraph "Processing Layer"
        G[Data Cleaner]
        H[Data Validator]
        I[Data Merger]
    end
    
    subgraph "Processed Data"
        J[Combined Rosters CSV]
        K[Rosters with Values CSV]
        L[Dashboard JSON]
    end
    
    subgraph "Analysis Layer"
        M[Jupyter Notebooks]
        N[Statistical Analysis]
    end
    
    subgraph "Visualization Layer"
        O[D3.js Dashboard]
        P[Interactive Charts]
    end
    
    subgraph "Deployment"
        Q[GitHub Pages / Vercel]
    end
    
    A -->|HTTP Requests| C
    B -->|HTTP Requests| D
    C -->|Scrape & Parse| E
    D -->|Scrape & Parse| F
    E --> G
    F --> G
    G --> H
    H --> I
    I --> J
    I --> K
    K --> L
    J --> M
    K --> M
    M --> N
    L --> O
    O --> P
    P --> Q
```

## Component Architecture

```mermaid
graph LR
    subgraph "Python Backend"
        A[Scrapers Module]
        B[Processing Module]
        C[Validation Module]
    end
    
    subgraph "Data Layer"
        D[Raw Data]
        E[Processed Data]
        F[JSON API]
    end
    
    subgraph "Frontend"
        G[HTML/CSS]
        H[D3.js Visualizations]
        I[Data Utilities]
    end
    
    A --> D
    D --> B
    B --> C
    C --> E
    E --> F
    F --> I
    I --> H
    G --> H
```

## Scraping Strategy

### Wikipedia Scraping Flow
```mermaid
sequenceDiagram
    participant S as Scraper
    participant W as Wikipedia
    participant P as Parser
    participant V as Validator
    participant D as Data Store
    
    S->>W: Request squad page
    W->>S: HTML response
    S->>P: Parse HTML tables
    P->>P: Extract roster data
    P->>V: Validate fields
    V->>V: Check completeness
    V->>D: Save to CSV
    D->>S: Confirm save
```

### Transfermarkt Scraping Flow
```mermaid
sequenceDiagram
    participant S as Scraper
    participant T as Transfermarkt
    participant M as Matcher
    participant D as Data Store
    
    S->>M: Get player list
    M->>M: Match player names
    loop For each player
        S->>T: Request player page
        T->>S: Dynamic content
        S->>S: Extract market value
        S->>S: Rate limit delay
    end
    S->>D: Save market values
```

## Dashboard Architecture

### Component Hierarchy
```mermaid
graph TD
    A[Dashboard App] --> B[Data Loader]
    A --> C[Filter Controls]
    A --> D[Visualization Container]
    
    D --> E[Age Distribution Chart]
    D --> F[Market Value Trends]
    D --> G[Club Country Map]
    D --> H[Position Analysis]
    D --> I[Squad Comparison]
    
    B --> J[JSON Data]
    C --> E
    C --> F
    C --> G
    C --> H
    C --> I
```

### Data Processing Pipeline

```mermaid
flowchart LR
    A[Raw Wikipedia HTML] --> B[Parse Tables]
    B --> C[Extract Fields]
    C --> D[Standardize Names]
    D --> E[Calculate Ages]
    E --> F[Add Flags]
    F --> G[Validate Data]
    G --> H[Save CSV]
    
    I[Raw Transfermarkt HTML] --> J[Extract Values]
    J --> K[Match Players]
    K --> L[Convert Currency]
    L --> M[Validate Values]
    M --> N[Save CSV]
    
    H --> O[Merge Datasets]
    N --> O
    O --> P[Final Dataset]
    P --> Q[Export JSON]
    Q --> R[Dashboard]
```

## Technology Stack Details

### Python Dependencies
- **beautifulsoup4** - HTML parsing
- **lxml** - Fast XML/HTML processing
- **requests** - HTTP client
- **selenium** or **playwright** - Dynamic content
- **pandas** - Data manipulation
- **numpy** - Numerical operations
- **jupyter** - Interactive notebooks
- **pytest** - Testing framework
- **black** - Code formatting
- **ruff** - Linting

### Frontend Dependencies
- **D3.js v7** - Data visualization
- **TopoJSON** - Geographic data
- **d3-tip** - Tooltips
- **Lodash** - Utility functions

### Development Tools
- **uv** - Python package manager
- **Git** - Version control
- **GitHub Actions** - CI/CD
- **Vite** - Build tool (optional)

## Deployment Architecture

```mermaid
graph TB
    A[GitHub Repository] --> B[GitHub Actions]
    B --> C[Build Process]
    C --> D[Static Assets]
    D --> E[GitHub Pages]
    D --> F[Vercel]
    
    G[Data Updates] --> A
    G --> B
```

## Security & Best Practices

### Scraping Ethics
- Respect robots.txt
- Implement rate limiting
- Cache responses
- Use appropriate user agents
- Handle errors gracefully

### Data Privacy
- No personal contact information
- Public data only
- Proper attribution
- License compliance

### Performance Optimization
- Lazy loading for large datasets
- Data pagination
- Efficient D3.js rendering
- Asset minification
- CDN for static assets

## Scalability Considerations

### Data Growth
- Current: ~8 tournaments × ~32 teams × ~23 players = ~5,888 records
- Future: Additional tournaments add ~736 records each
- Market value data: Similar scale

### Performance Targets
- Dashboard load time: < 3 seconds
- Visualization render: < 1 second
- Data file size: < 2MB compressed
- Browser support: Modern browsers (ES6+)

## Error Handling Strategy

```mermaid
flowchart TD
    A[Scraping Request] --> B{Success?}
    B -->|Yes| C[Parse Data]
    B -->|No| D[Log Error]
    D --> E[Retry Logic]
    E --> F{Max Retries?}
    F -->|No| A
    F -->|Yes| G[Skip & Continue]
    
    C --> H{Valid Data?}
    H -->|Yes| I[Save Data]
    H -->|No| J[Log Warning]
    J --> K[Manual Review]
```

## Monitoring & Logging

### Logging Levels
- **INFO**: Successful operations
- **WARNING**: Missing data, retries
- **ERROR**: Failed requests, parsing errors
- **DEBUG**: Detailed scraping info

### Metrics to Track
- Scraping success rate
- Data completeness percentage
- Processing time per year
- Dashboard load performance
- User interactions (optional)