// Country code mapping for flag URLs
const countryFlags = {
    'Argentina': 'ar', 'Australia': 'au', 'Austria': 'at', 'Belgium': 'be', 'Brazil': 'br',
    'Bulgaria': 'bg', 'Cameroon': 'cm', 'Canada': 'ca', 'Chile': 'cl', 'Colombia': 'co',
    'Costa Rica': 'cr', 'Croatia': 'hr', 'Denmark': 'dk', 'Ecuador': 'ec', 'England': 'gb-eng',
    'France': 'fr', 'Germany': 'de', 'Ghana': 'gh', 'Greece': 'gr', 'Honduras': 'hn',
    'Iran': 'ir', 'Italy': 'it', 'Ivory Coast': 'ci', 'Jamaica': 'jm', 'Japan': 'jp',
    'Mexico': 'mx', 'Morocco': 'ma', 'Netherlands': 'nl', 'Nigeria': 'ng', 'Norway': 'no',
    'Paraguay': 'py', 'Peru': 'pe', 'Poland': 'pl', 'Portugal': 'pt', 'Qatar': 'qa',
    'Romania': 'ro', 'Russia': 'ru', 'Saudi Arabia': 'sa', 'Scotland': 'gb-sct', 'Senegal': 'sn',
    'Serbia': 'rs', 'South Africa': 'za', 'South Korea': 'kr', 'Spain': 'es', 'Sweden': 'se',
    'Switzerland': 'ch', 'Tunisia': 'tn', 'Turkey': 'tr', 'Ukraine': 'ua', 'United States': 'us',
    'Uruguay': 'uy', 'Wales': 'gb-wls', 'FR Yugoslavia': 'rs', 'Iceland': 'is', 'Panama': 'pa',
    'Bosnia and Herzegovina': 'ba', 'Algeria': 'dz', 'New Zealand': 'nz', 'North Korea': 'kp',
    'Slovakia': 'sk', 'Trinidad and Tobago': 'tt', 'Togo': 'tg', 'Angola': 'ao',
    'Serbia and Montenegro': 'rs', 'Uzbekistan': 'uz', 'Iraq': 'iq', 'Haiti': 'ht',
    'Egypt': 'eg', 'Czech Republic': 'cz', 'China PR': 'cn', 'Slovenia': 'si',
    'Republic of Ireland': 'ie', 'Jordan': 'jo', 'DR Congo': 'cd', 'Cape Verde': 'cv',
    'Curaçao': 'cw', 'Curacao': 'cw'
};

// Map football association names to country names for home league calculation
const associationToCountry = {
    'United States Soccer Federation': 'United States',
    'The Football Association': 'England',
    'German Football Association': 'Germany',
    'French Football Federation': 'France',
    'Royal Dutch Football Association': 'Netherlands',
    'Italian Football Federation': 'Italy',
    'Scottish Football Association': 'Scotland',
    'Canadian Soccer Association': 'Canada',
    'Royal Spanish Football Federation': 'Spain',
    'Mexican Football Federation': 'Mexico',
    'Saudi Arabian Football Federation': 'Saudi Arabia',
    'Argentine Football Association': 'Argentina',
    'Brazilian Football Confederation': 'Brazil',
    'Portuguese Football Federation': 'Portugal',
    'Royal Belgian Football Association': 'Belgium',
    'Swiss Football Association': 'Switzerland',
    'Austrian Football Association': 'Austria',
    'Danish Football Association': 'Denmark',
    'Swedish Football Association': 'Sweden',
    'Norwegian Football Federation': 'Norway',
    'Polish Football Association': 'Poland',
    'Turkish Football Federation': 'Turkey',
    'Hellenic Football Federation': 'Greece',
    'Croatian Football Federation': 'Croatia',
    'Football Association of Serbia': 'Serbia',
    'Romanian Football Federation': 'Romania',
    'Bulgarian Football Union': 'Bulgaria',
    'Football Association of Slovenia': 'Slovenia',
    'Slovak Football Association': 'Slovakia',
    'Japan Football Association': 'Japan',
    'Korea Football Association': 'South Korea',
    'Chinese Football Association': 'China PR',
    'Football Australia': 'Australia',
    'New Zealand Football': 'New Zealand',
    'Qatar Football Association': 'Qatar',
    'Football Federation Islamic Republic of Iran': 'Iran',
    'Iraq Football Association': 'Iraq',
    'Royal Moroccan Football Federation': 'Morocco',
    'Tunisian Football Federation': 'Tunisia',
    'Egyptian Football Association': 'Egypt',
    'Algerian Football Federation': 'Algeria',
    'Ghana Football Association': 'Ghana',
    'South African Football Association': 'South Africa',
    'Uruguayan Football Association': 'Uruguay',
    'Football Federation of Chile': 'Chile',
    'Colombian Football Federation': 'Colombia',
    'Paraguayan Football Association': 'Paraguay',
    'Ecuadorian Football Federation': 'Ecuador',
    'Costa Rican Football Federation': 'Costa Rica',
    'National Autonomous Federation of Football of Honduras': 'Honduras',
    'Panamanian Football Federation': 'Panama',
    'Haitian Football Federation': 'Haiti',
    'Football Association of Wales': 'Wales',
    'Football Association of Bosnia and Herzegovina': 'Bosnia and Herzegovina',
    'Uzbekistan Football Association': 'Uzbekistan',
    'Jordan Football Association': 'Jordan',
    'Football Association of Ireland': 'Republic of Ireland',
    'Hungarian Football Federation': 'Hungary',
    'Football Association of the Czech Republic': 'Czech Republic',
    'Russian Football Union': 'Russia',
    'United Arab Emirates Football Association': 'United Arab Emirates',
    'Israel Football Association': 'Israel',
    'Venezuelan Football Federation': 'Venezuela',
    'Kazakhstan Football Federation': 'Kazakhstan',
    'Association of Football Federations of Azerbaijan': 'Azerbaijan',
    'Football Federation of Armenia': 'Armenia',
    'Cyprus Football Association': 'Cyprus',
    'Football Association of Finland': 'Finland',
    'Football Association of Thailand': 'Thailand',
    'Football Association of Malaysia': 'Malaysia',
    'Football Association of Indonesia': 'Indonesia'
};

let currentMetric = 'caps';
let data = [];
let allRosterData = []; // Store raw roster data for country details
let tournamentResults = {}; // Store tournament results by year-country

// Metric descriptions
const metricDescriptions = {
    age: "Average age of players in each country's World Cup squad. Younger teams may have more energy and potential, while older teams often bring experience and tactical maturity.",
    caps: "Average number of international appearances (caps) per player in each squad. Higher caps indicate more experienced players who have represented their country frequently.",
    homeleague: "Percentage of players in each squad who play for clubs in their home country's league. Higher percentages may indicate strong domestic leagues or less international player movement.",
    relativevalue: "Relative market value (z-score) compared to other teams in the same World Cup. Shows which squads were expensive or cheap relative to their tournament peers. Positive values indicate above-average squads, negative values indicate below-average. Data available from 2006 onwards.",
    totalvalue: "Total squad market value in millions of euros. Represents the combined worth of all players in the squad. Data available from 2006 onwards."
};

// Load and process data
async function loadData() {
    // Load tournament results
    const resultsResponse = await fetch('data/processed/tournament_results.csv');
    const resultsText = await resultsResponse.text();
    const resultsRows = d3.csvParse(resultsText);
    
    // Create lookup object for tournament results
    resultsRows.forEach(row => {
        const key = `${row.Year}-${row.Country}`;
        tournamentResults[key] = row.Display;
    });
    
    const response = await fetch('data/processed/rosters_with_market_values.csv');
    const csvText = await response.text();
    const rows = d3.csvParse(csvText);
    
    // Store all roster data for country details
    allRosterData = rows;
    
    // Calculate team averages by year and country
    const teamStats = d3.rollup(
        rows.filter(d => d.Age && d.Caps),
        v => {
            // Calculate market values (convert from EUR to millions)
            const playersWithValues = v.filter(d => d.Market_Value_EUR && d.Market_Value_EUR !== '' && !isNaN(+d.Market_Value_EUR));
            const avgMarketValue = playersWithValues.length > 0
                ? d3.mean(playersWithValues, d => +d.Market_Value_EUR) / 1000000
                : null;
            const totalMarketValue = playersWithValues.length > 0
                ? d3.sum(playersWithValues, d => +d.Market_Value_EUR) / 1000000
                : null;
            
            // Calculate home league percentage by mapping Club_Country to actual country
            const homeLeaguePlayers = v.filter(d => {
                const clubCountry = associationToCountry[d.Club_Country] || d.Club_Country;
                return clubCountry === d.Country;
            }).length;
            
            return {
                avgAge: d3.mean(v, d => +d.Age),
                avgCaps: d3.mean(v, d => +d.Caps),
                homeLeaguePct: (homeLeaguePlayers / v.length) * 100,
                avgMarketValue: avgMarketValue,
                totalMarketValue: totalMarketValue,
                country: v[0].Country,
                year: +v[0].Year
            };
        },
        d => d.Year,
        d => d.Country
    );
    
    // Flatten to array
    data = [];
    teamStats.forEach((countries, year) => {
        countries.forEach((stats, country) => {
            data.push({
                year: stats.year,
                country: stats.country,
                avgAge: stats.avgAge,
                avgCaps: stats.avgCaps,
                homeLeaguePct: stats.homeLeaguePct,
                avgMarketValue: stats.avgMarketValue,
                totalMarketValue: stats.totalMarketValue
            });
        });
    });
    
    // Calculate z-scores for average market value by year
    const yearGroups = d3.group(data, d => d.year);
    yearGroups.forEach((yearData, year) => {
        const validValues = yearData.filter(d => d.avgMarketValue !== null).map(d => d.avgMarketValue);
        if (validValues.length > 0) {
            const mean = d3.mean(validValues);
            const stdDev = d3.deviation(validValues);
            
            yearData.forEach(d => {
                if (d.avgMarketValue !== null && stdDev > 0) {
                    d.relativeMarketValue = (d.avgMarketValue - mean) / stdDev;
                } else {
                    d.relativeMarketValue = null;
                }
            });
        }
    });
    
    // Delay initial render slightly to ensure layout is stable
    setTimeout(() => {
        renderChart();
        updateMetricDescription();
    }, 100);
}

// Update metric description panel
function updateMetricDescription() {
    document.getElementById('descriptionText').textContent = metricDescriptions[currentMetric];
}

// Update country details panel
function updateCountryDetails(country, year) {
    const detailsContent = document.getElementById('countryDetailsContent');
    
    // Get all data for this country across all years
    const countryData = data.filter(d => d.country === country);
    
    if (countryData.length === 0) {
        detailsContent.innerHTML = '<div class="no-selection">No data available</div>';
        return;
    }
    
    // Sort by year descending (most recent first)
    countryData.sort((a, b) => b.year - a.year);
    
    // Build HTML table without scrolling
    let html = `
        <div class="country-stats">
            <h4 style="margin-bottom: 8px; color: #333; font-size: 14px;">${country}</h4>
            <table>
                <thead>
                    <tr>
                        <th>Year</th>
                        <th>Caps</th>
                        <th>Age</th>
                        <th>Home%</th>
                        <th>Total€</th>
                        <th>Avg€</th>
                        <th>Rel</th>
                        <th>Finish</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    countryData.forEach(d => {
        const isCurrentYear = d.year === year;
        const rowStyle = isCurrentYear ? 'background: #e3f2fd; font-weight: 600;' : '';
        const avgValueStr = d.avgMarketValue ? `€${d.avgMarketValue.toFixed(1)}M` : 'N/A';
        const totalValueStr = d.totalMarketValue ? `€${d.totalMarketValue.toFixed(0)}M` : 'N/A';
        const relValueStr = d.relativeMarketValue !== null && d.relativeMarketValue !== undefined
            ? d.relativeMarketValue.toFixed(2)
            : 'N/A';
        
        // Get tournament finish
        const resultKey = `${d.year}-${d.country}`;
        const finish = tournamentResults[resultKey] || '-';
        
        html += `
            <tr style="${rowStyle}">
                <td>${d.year}</td>
                <td>${d.avgCaps.toFixed(1)}</td>
                <td>${d.avgAge.toFixed(1)}</td>
                <td>${d.homeLeaguePct.toFixed(1)}%</td>
                <td>${totalValueStr}</td>
                <td>${avgValueStr}</td>
                <td>${relValueStr}</td>
                <td>${finish}</td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    detailsContent.innerHTML = html;
}

// Clear country details
function clearCountryDetails() {
    document.getElementById('countryDetailsContent').innerHTML =
        '<div class="no-selection">Hover over a country flag to see detailed statistics</div>';
}

function renderChart() {
    // Clear existing chart
    d3.select('#chart').selectAll('*').remove();
    
    // Get container dimensions for responsive sizing
    const container = document.getElementById('chart');
    const containerWidth = container.clientWidth;
    
    console.log('Container width:', containerWidth);
    
    // Calculate available height (viewport height minus header and padding)
    const viewportHeight = window.innerHeight;
    const isMobile = window.innerWidth <= 768;
    
    // Adjust margins for mobile devices - smaller bottom margin for smaller logos
    const margin = isMobile
        ? {top: 0, right: 30, bottom: 80, left: 50}  // No top margin to move chart higher
        : {top: 40, right: 60, bottom: 160, left: 80}; // Original margins on desktop
    
    const availableHeight = viewportHeight - 200;
    
    const width = Math.max(600, containerWidth - margin.left - margin.right);
    const height = Math.min(availableHeight - margin.top - margin.bottom, width * 0.6);
    
    console.log('Chart dimensions:', width, height);
    
    const svg = d3.select('#chart')
        .append('svg')
        .attr('width', '100%')
        .attr('height', height + margin.top + margin.bottom)
        .attr('viewBox', `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
        .attr('preserveAspectRatio', 'xMidYMid meet')
        .style('display', 'block')
        .style('margin', '0 auto')
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // Get unique years
    const years = [...new Set(data.map(d => d.year))].sort();
    
    // Scales - SWITCHED: X-axis is years, Y-axis is values
    const xScale = d3.scaleBand()
        .domain(years)
        .range([0, width])
        .padding(0.3);
    
    // Set appropriate Y-axis scale based on metric
    let yDomain;
    if (currentMetric === 'age') {
        yDomain = [23, 31];
    } else if (currentMetric === 'caps') {
        yDomain = [10, 65];
    } else if (currentMetric === 'homeleague') {
        yDomain = [0, 100];
    } else if (currentMetric === 'relativevalue') {
        // Filter out null values for market value metrics
        const validData = data.filter(d => d.relativeMarketValue !== null);
        if (validData.length > 0) {
            const minValue = d3.min(validData, d => d.relativeMarketValue);
            const maxValue = d3.max(validData, d => d.relativeMarketValue);
            yDomain = [Math.floor(minValue * 1.1), Math.ceil(maxValue * 1.1)]; // Add 10% padding
        } else {
            yDomain = [-2.5, 2.5]; // Default z-score range
        }
    } else if (currentMetric === 'totalvalue') {
        const validData = data.filter(d => d.totalMarketValue !== null);
        if (validData.length > 0) {
            const maxValue = d3.max(validData, d => d.totalMarketValue);
            yDomain = [0, Math.ceil(maxValue * 1.1)]; // Add 10% padding
        } else {
            yDomain = [0, 1000]; // Default if no data
        }
    }
    
    const yScale = d3.scaleLinear()
        .domain(yDomain)
        .range([height, 0]);
    
    // Add World Cup logos on X-axis (bottom) - smaller on mobile
    const logoSize = isMobile ? 50 : 100;  // Half size on mobile
    const logoYOffset = isMobile ? 15 : 30;
    const textYOffset = isMobile ? 70 : 145;
    
    years.forEach(year => {
        svg.append('image')
            .attr('href', `logos/wc_${year}.png`)
            .attr('x', xScale(year) + xScale.bandwidth()/2 - logoSize/2)
            .attr('y', height + logoYOffset)
            .attr('width', logoSize)
            .attr('height', logoSize);
        
        svg.append('text')
            .attr('x', xScale(year) + xScale.bandwidth()/2)
            .attr('y', height + textYOffset)
            .attr('text-anchor', 'middle')
            .style('font-size', isMobile ? '12px' : '14px')
            .style('font-weight', 'bold')
            .text(year);
    });
    
    // Y-axis
    svg.append('g')
        .call(d3.axisLeft(yScale).ticks(10))
        .selectAll('text')
        .style('font-size', '12px');
    
    // Y-axis label
    let yLabel;
    if (currentMetric === 'age') {
        yLabel = 'Average Age (years)';
    } else if (currentMetric === 'caps') {
        yLabel = 'Average Caps';
    } else if (currentMetric === 'homeleague') {
        yLabel = '% Players from Home League';
    } else if (currentMetric === 'relativevalue') {
        yLabel = 'Relative Market Value (z-score)';
    } else if (currentMetric === 'totalvalue') {
        yLabel = 'Total Squad Value (€M)';
    }
    
    svg.append('text')
        .attr('class', 'axis-label')
        .attr('transform', 'rotate(-90)')
        .attr('x', -height / 2)
        .attr('y', -50)
        .attr('text-anchor', 'middle')
        .text(yLabel);
    
    // Tooltip
    const tooltip = d3.select('.tooltip');
    
    // Add country flags as data points with jitter to prevent overlap
    const flagSize = 24;
    
    // Simple positioning with slight jitter for overlaps
    const dataWithJitter = data.map((d, i) => {
        let value;
        if (currentMetric === 'age') {
            value = d.avgAge;
        } else if (currentMetric === 'caps') {
            value = d.avgCaps;
        } else if (currentMetric === 'homeleague') {
            value = d.homeLeaguePct;
        } else if (currentMetric === 'relativevalue') {
            value = d.relativeMarketValue;
        } else if (currentMetric === 'totalvalue') {
            value = d.totalMarketValue;
        }
        
        // Skip if value is null (no market value data)
        if (value === null || value === undefined) {
            return null;
        }
        
        const baseX = xScale(d.year) + xScale.bandwidth()/2;
        
        // Find other flags in same year with similar values
        let threshold;
        if (currentMetric === 'homeleague') {
            threshold = 2;
        } else if (currentMetric === 'relativevalue') {
            threshold = 0.3; // z-score threshold
        } else if (currentMetric === 'totalvalue') {
            threshold = 20; // 20M EUR threshold
        } else {
            threshold = 0.3;
        }
        
        const overlapping = data.filter((other, j) => {
            if (i >= j) return false; // Only check previous items
            let otherValue;
            if (currentMetric === 'age') {
                otherValue = other.avgAge;
            } else if (currentMetric === 'caps') {
                otherValue = other.avgCaps;
            } else if (currentMetric === 'homeleague') {
                otherValue = other.homeLeaguePct;
            } else if (currentMetric === 'relativevalue') {
                otherValue = other.relativeMarketValue;
            } else if (currentMetric === 'totalvalue') {
                otherValue = other.totalMarketValue;
            }
            
            // Skip if either value is null
            if (otherValue === null || otherValue === undefined) return false;
            
            return other.year === d.year && Math.abs(value - otherValue) < threshold;
        });
        
        // Add small horizontal jitter based on number of overlaps
        const jitterAmount = overlapping.length * 4;
        const jitter = (i % 2 === 0 ? 1 : -1) * jitterAmount;
        
        return {
            ...d,
            displayX: baseX + jitter,
            displayY: yScale(value),
            baseX: baseX,
            clusterSize: overlapping.length + 1  // Store cluster size for hover effect
        };
    }).filter(d => d !== null); // Filter out null values (missing market data)
    
    svg.selectAll('.flag')
        .data(dataWithJitter)
        .enter()
        .append('image')
        .attr('class', 'flag')
        .attr('href', d => {
            const code = countryFlags[d.country] || 'un';
            return `https://flagcdn.com/w40/${code}.png`;
        })
        .attr('x', d => d.displayX - flagSize/2)
        .attr('y', d => d.displayY - flagSize/2)
        .attr('width', flagSize)
        .attr('height', flagSize)
        .style('cursor', 'pointer')
        .on('error', function(event, d) {
            // Fallback for missing flags - show country code
            d3.select(this.parentNode)
                .append('text')
                .attr('x', d.displayX)
                .attr('y', d.displayY)
                .attr('text-anchor', 'middle')
                .attr('dominant-baseline', 'middle')
                .style('font-size', '10px')
                .style('font-weight', 'bold')
                .text(d.country.substring(0, 3).toUpperCase());
        })
        .on('click', function(event, d) {
            // First, handle cluster expansion if this flag is part of a cluster
            if (d.clusterSize > 1) {
                // Find all flags in the same cluster (same year, similar value)
                let threshold;
                if (currentMetric === 'homeleague') {
                    threshold = 2;
                } else if (currentMetric === 'relativevalue') {
                    threshold = 0.3;
                } else if (currentMetric === 'totalvalue') {
                    threshold = 20;
                } else {
                    threshold = 0.3;
                }
                
                let value;
                if (currentMetric === 'age') {
                    value = d.avgAge;
                } else if (currentMetric === 'caps') {
                    value = d.avgCaps;
                } else if (currentMetric === 'homeleague') {
                    value = d.homeLeaguePct;
                } else if (currentMetric === 'relativevalue') {
                    value = d.relativeMarketValue;
                } else if (currentMetric === 'totalvalue') {
                    value = d.totalMarketValue;
                }
                
                const clusterFlags = svg.selectAll('.flag')
                    .filter(function(other) {
                        let otherValue;
                        if (currentMetric === 'age') {
                            otherValue = other.avgAge;
                        } else if (currentMetric === 'caps') {
                            otherValue = other.avgCaps;
                        } else if (currentMetric === 'homeleague') {
                            otherValue = other.homeLeaguePct;
                        } else if (currentMetric === 'relativevalue') {
                            otherValue = other.relativeMarketValue;
                        } else if (currentMetric === 'totalvalue') {
                            otherValue = other.totalMarketValue;
                        }
                        return other.year === d.year && Math.abs(value - otherValue) < threshold;
                    });
                
                // Expand cluster horizontally
                const clusterData = clusterFlags.data();
                const spacing = 28;
                const totalWidth = (clusterData.length - 1) * spacing;
                const startX = d.baseX - totalWidth / 2;
                
                clusterFlags
                    .transition()
                    .duration(200)
                    .attr('x', (cd, i) => startX + (i * spacing) - flagSize/2)
                    .attr('width', flagSize)
                    .attr('height', flagSize);
            }
            
            // Then, enlarge all instances of this country across all years and bring to front
            svg.selectAll('.flag')
                .filter(other => other.country === d.country)
                .each(function() {
                    // Move to front by re-appending to parent
                    this.parentNode.appendChild(this);
                })
                .transition()
                .duration(200)
                .attr('width', flagSize * 1.5)
                .attr('height', flagSize * 1.5)
                .attr('x', fd => fd.displayX - (flagSize * 1.5)/2)
                .attr('y', fd => fd.displayY - (flagSize * 1.5)/2);
            
            // Update country details panel (persistent on click)
            updateCountryDetails(d.country, d.year);
        })
        .on('mouseover', function(event, d) {
            // First, handle cluster expansion if this flag is part of a cluster
            if (d.clusterSize > 1) {
                // Find all flags in the same cluster (same year, similar value)
                let threshold;
                if (currentMetric === 'homeleague') {
                    threshold = 2;
                } else if (currentMetric === 'relativevalue') {
                    threshold = 0.3;
                } else if (currentMetric === 'totalvalue') {
                    threshold = 20;
                } else {
                    threshold = 0.3;
                }
                
                let value;
                if (currentMetric === 'age') {
                    value = d.avgAge;
                } else if (currentMetric === 'caps') {
                    value = d.avgCaps;
                } else if (currentMetric === 'homeleague') {
                    value = d.homeLeaguePct;
                } else if (currentMetric === 'relativevalue') {
                    value = d.relativeMarketValue;
                } else if (currentMetric === 'totalvalue') {
                    value = d.totalMarketValue;
                }
                
                const clusterFlags = svg.selectAll('.flag')
                    .filter(function(other) {
                        let otherValue;
                        if (currentMetric === 'age') {
                            otherValue = other.avgAge;
                        } else if (currentMetric === 'caps') {
                            otherValue = other.avgCaps;
                        } else if (currentMetric === 'homeleague') {
                            otherValue = other.homeLeaguePct;
                        } else if (currentMetric === 'relativevalue') {
                            otherValue = other.relativeMarketValue;
                        } else if (currentMetric === 'totalvalue') {
                            otherValue = other.totalMarketValue;
                        }
                        return other.year === d.year && Math.abs(value - otherValue) < threshold;
                    });
                
                // Expand cluster horizontally
                const clusterData = clusterFlags.data();
                const spacing = 28;
                const totalWidth = (clusterData.length - 1) * spacing;
                const startX = d.baseX - totalWidth / 2;
                
                clusterFlags
                    .transition()
                    .duration(200)
                    .attr('x', (cd, i) => startX + (i * spacing) - flagSize/2)
                    .attr('width', flagSize)
                    .attr('height', flagSize);
            }
            
            // Enlarge all instances of this country across all years and bring to front
            svg.selectAll('.flag')
                .filter(other => other.country === d.country)
                .each(function() {
                    // Move to front by re-appending to parent
                    this.parentNode.appendChild(this);
                })
                .transition()
                .duration(200)
                .attr('width', flagSize * 1.5)
                .attr('height', flagSize * 1.5)
                .attr('x', fd => fd.displayX - (flagSize * 1.5)/2)
                .attr('y', fd => fd.displayY - (flagSize * 1.5)/2);
            
            // Show tooltip on hover
            let value;
            if (currentMetric === 'age') {
                value = d.avgAge.toFixed(1) + ' years';
            } else if (currentMetric === 'caps') {
                value = d.avgCaps.toFixed(1) + ' caps';
            } else if (currentMetric === 'homeleague') {
                value = d.homeLeaguePct.toFixed(1) + '%';
            } else if (currentMetric === 'relativevalue') {
                value = d.relativeMarketValue !== null ? d.relativeMarketValue.toFixed(2) : 'N/A';
            } else if (currentMetric === 'totalvalue') {
                value = d.totalMarketValue ? '€' + d.totalMarketValue.toFixed(0) + 'M' : 'N/A';
            }
            
            tooltip
                .style('opacity', 1)
                .html(`<strong>${d.country}</strong><br>${d.year}<br>${value}`)
                .style('left', (event.pageX + 25) + 'px')
                .style('top', (event.pageY - 10) + 'px');
        })
        .on('mouseout', function(event, d) {
            // Return all flags to their jittered positions
            svg.selectAll('.flag')
                .transition()
                .duration(200)
                .attr('width', flagSize)
                .attr('height', flagSize)
                .attr('x', fd => fd.displayX - flagSize/2)
                .attr('y', fd => fd.displayY - flagSize/2);
            
            tooltip.style('opacity', 0);
        });
}

// Dropdown functionality
const dropdownButton = document.getElementById('metricDropdown');
const dropdownMenu = document.getElementById('dropdownMenu');
const selectedMetricSpan = document.getElementById('selectedMetric');
const dropdownArrow = document.querySelector('.dropdown-arrow');

dropdownButton.addEventListener('click', function(e) {
    e.stopPropagation();
    dropdownMenu.classList.toggle('open');
    dropdownArrow.classList.toggle('open');
});

// Close dropdown when clicking outside
document.addEventListener('click', function() {
    dropdownMenu.classList.remove('open');
    dropdownArrow.classList.remove('open');
});

// Handle metric selection
document.querySelectorAll('.dropdown-item').forEach(item => {
    item.addEventListener('click', function() {
        const metric = this.dataset.metric;
        const metricText = this.textContent;
        
        currentMetric = metric;
        selectedMetricSpan.textContent = metricText;
        
        dropdownMenu.classList.remove('open');
        dropdownArrow.classList.remove('open');
        
        renderChart();
        updateMetricDescription();
    });
});

// Initialize
loadData();

// Add window resize listener with debouncing
let resizeTimeout;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        if (data.length > 0) {
            renderChart();
        }
    }, 250);
});

// Made with Bob
