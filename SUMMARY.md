# 📋 Project Summary: AI Material Selector

## Overview
The AI Material Selector is an advanced engineering tool designed to streamline the process of material selection for manufacturing and industrial applications. It bridges the gap between raw material data and complex engineering requirements by using AI to analyze constraints, physical properties, and natural language prompts.

## Key Development Milestones
1. **Core Data Engine:** Established a solid foundation using Pandas to parse and filter a comprehensive CSV database of material properties (Yield Strength, Density, Max Operating Temperature, Cost, etc.).
2. **AI Integration:** Successfully integrated the Google Gemini API to act as a reasoning engine. The AI not only matches materials based on numeric constraints but can reason about trade-offs (e.g., strength-to-weight ratio vs. cost).
3. **Advanced Pricing Models:** Built a flexible cost engine that calculates final part prices based on volume/density, pulling data from CSVs, AI estimations, or live MetalPrice API lookups.
4. **Data Visualization:** Integrated Plotly to provide rich telemetry, including Radar Charts for comparing candidates, Scatter Plots for performance mapping, and Property Heatmaps.
5. **Tactical UI Overhaul:** Refined the interface from a standard Streamlit layout into a premium, tactical dashboard. We implemented a 4-column layout, customized CSS for glassmorphism and sharp borders, and deployed a dynamic Progress Tracker.
6. **Vector Templates:** Allowed users to save and reuse complex engineering prompts via local JSON storage, drastically speeding up repetitive workflows.

## Design Philosophy
The application was built with a "Defense/Industrial" aesthetic, prioritizing:
- **Clarity over Clutter:** Utilizing `JetBrains Mono` for data and removing excessive white space.
- **Speed (Lite Mode):** Offering a stripped-down mode for rapid, single-answer inferences.
- **Deep Analysis (Advanced Mode):** Offering full constraint manipulation and chat-based follow-ups for deep engineering research.

## Next Steps / Future Roadmap
- Expand the `materials.csv` database to include advanced composites and additive manufacturing materials.
- Implement user account logins and cloud template synchronization.
- Integrate 3D STL mesh viewing directly in the Streamlit comparative tab.
