import base64
from io import BytesIO
import plotly.io as pio

def _fig_to_base64(fig):
    if fig is None:
        return ""
    
    buf = BytesIO()
    try:
        # Standard Matplotlib figure export
        fig.savefig(buf, format="png", bbox_inches="tight")
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        return f"data:image/png;base64,{data}"
    except Exception as e:
        print(f"Error converting figure for report: {e}")
        return ""

def generate_html_report(df_info, stats_df, fig_missing, fig_corr, auto_summary, insights, recommendations):
    # IMPROVED FEATURE: Enhanced layout and AI integration
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>DataWhisper - Analysis Report</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px auto; max-width: 1000px; color: #333; line-height: 1.6; background-color: #f8fafc; }}
            h1, h2, h3 {{ color: #1e293b; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }}
            h1 {{ text-align: center; margin-bottom: 40px; color: #818cf8; border-bottom: none; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; font-size: 0.9em; background: #fff; }}
            th, td {{ border: 1px solid #e2e8f0; padding: 12px; text-align: left; }}
            th {{ background-color: #f1f5f9; color: #475569; font-weight: 600; }}
            tr:nth-child(even) {{ background-color: #f8fafc; }}
            .img-container {{ margin: 30px 0; text-align: center; background: #fff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
            img {{ max-width: 100%; height: auto; border-radius: 8px; }}
            .section {{ margin-bottom: 40px; background: #fff; padding: 35px; border-radius: 12px; box-shadow: 0 1px 3px 0 rgba(0,0,0,0.1); border: 1px solid #e2e8f0; }}
            .markdown-content {{ white-space: pre-wrap; background: #f1f5f9; padding: 25px; border-left: 5px solid #818cf8; font-size: 1em; border-radius: 4px; color: #334155; }}
            .metric-box {{ display: inline-block; width: 30%; background: #f8fafc; padding: 20px; margin: 1%; text-align: center; border-radius: 10px; border: 1px solid #e2e8f0; }}
            .metric-value {{ font-size: 1.8em; font-weight: bold; color: #818cf8; }}
            .metric-label {{ color: #64748b; text-transform: uppercase; font-size: 0.75em; letter-spacing: 1.5px; font-weight: 600; }}
            .ai-badge {{ background: #818cf8; color: white; padding: 4px 12px; border-radius: 99px; font-size: 0.8em; font-weight: bold; margin-bottom: 10px; display: inline-block; }}
        </style>
    </head>
    <body>
        <h1>📊 DataWhisper Analysis Report</h1>
        
        <div class="section">
            <h2><span class="ai-badge">AI</span> Executive Summary</h2>
            <div class="markdown-content">
                {auto_summary if auto_summary else 'No auto-summary generated.'}
            </div>
        </div>

        <div class="section">
            <h2>Dataset Overview</h2>
            <div style="text-align: center; margin-top: 20px;">
                <div class="metric-box">
                    <div class="metric-value">{df_info['shape'][0]}</div>
                    <div class="metric-label">Total Rows</div>
                </div>
                <div class="metric-box">
                    <div class="metric-value">{df_info['shape'][1]}</div>
                    <div class="metric-label">Total Columns</div>
                </div>
                <div class="metric-box">
                    <div class="metric-value">{sum(df_info['missing_values'].values())}</div>
                    <div class="metric-label">Missing Values</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Summary Statistics</h2>
            <div style="overflow-x: auto;">
                {stats_df.to_html(classes='', border=0)}
            </div>
        </div>
        
        <div class="section">
            <h2>Key Visualizations</h2>
    """
    if fig_missing:
        html += f'<div class="img-container"><h3>Missing Values Heatmap</h3><img src="{_fig_to_base64(fig_missing)}"/></div>'
    if fig_corr:
        html += f'<div class="img-container"><h3>Correlation Matrix</h3><img src="{_fig_to_base64(fig_corr)}"/></div>'
        
    html += f"""
        </div>
        
        <div class="section">
            <h2><span class="ai-badge">AI</span> Deep Insights</h2>
            <div class="markdown-content">
                {insights if insights else 'Deep insights not generated in this session.'}
            </div>
        </div>
        
        <div class="section">
            <h2>Recommendations</h2>
            <div class="markdown-content">
                {recommendations if recommendations else 'Recommendations not generated in this session.'}
            </div>
        </div>
        
        <div style="text-align: center; color: #94a3b8; font-size: 0.85em; margin-top: 60px; padding-bottom: 40px;">
            <p>Generated by DataWhisper AI | {df_info['columns'][0]} Analysis Report</p>
        </div>
    </body>
    </html>
    """
    return html
