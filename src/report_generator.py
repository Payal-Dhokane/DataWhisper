import base64
from io import BytesIO
import plotly.io as pio

def _fig_to_base64(fig):
    if fig is None:
        return ""
    
    buf = BytesIO()
    try:
        # Check if it's a Plotly figure
        if hasattr(fig, "to_image"):
            try:
                # Plotly figure - needs kaleido installed
                img_bytes = fig.to_image(format="png", engine="kaleido")
                data = base64.b64encode(img_bytes).decode("ascii")
                return f"data:image/png;base64,{data}"
            except Exception as e:
                # If kaleido fails, try to return an interactive HTML div if possible?
                # For simplicity in PDF-like HTML, we just log and return empty
                print(f"Kaleido failure: {e}")
                return ""
        else:
            # Matplotlib figure
            fig.savefig(buf, format="png", bbox_inches="tight")
            data = base64.b64encode(buf.getbuffer()).decode("ascii")
            return f"data:image/png;base64,{data}"
    except Exception as e:
        print(f"Error converting figure for report: {e}")
        return ""

def generate_html_report(df_info, stats_df, fig_missing, fig_corr, insights, recommendations):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>DataWhisper - Analysis Report</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px auto; max-width: 1000px; color: #333; line-height: 1.6; }}
            h1, h2, h3 {{ color: #2C3E50; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
            h1 {{ text-align: center; margin-bottom: 40px; color: #1abc9c; border-bottom: none; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; font-size: 0.9em; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #f8f9fa; color: #333; font-weight: bold; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .img-container {{ margin: 30px 0; text-align: center; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
            img {{ max-width: 100%; height: auto; border: 1px solid #eee; border-radius: 4px; }}
            .section {{ margin-bottom: 50px; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.02); }}
            .markdown-content {{ white-space: pre-wrap; background: #fdfdfd; padding: 20px; border-left: 4px solid #3498db; font-size: 1.05em; }}
            body {{ background-color: #f4f7f6; }}
            .metric-box {{ display: inline-block; width: 30%; background: #fff; padding: 20px; margin: 1%; text-align: center; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
            .metric-value {{ font-size: 2em; font-weight: bold; color: #2980b9; }}
            .metric-label {{ color: #7f8c8d; text-transform: uppercase; font-size: 0.85em; letter-spacing: 1px; }}
        </style>
    </head>
    <body>
        <h1>📊 DataWhisper Analysis Report</h1>
        
        <div class="section">
            <h2>Dataset Overview</h2>
            <div style="text-align: center;">
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
        
    html += """
        </div>
        
        <div class="section">
            <h2>AI Insights</h2>
            <div class="markdown-content">
    """
    
    html += f"{insights if insights else 'No insights generated. Provide an API key and visit the AI Insights tab before generating the report.'}"
    
    html += """
            </div>
        </div>
        
        <div class="section">
            <h2>Recommendations for Next Steps</h2>
            <div class="markdown-content">
    """
    html += f"{recommendations if recommendations else 'No recommendations generated. Provide an API key and visit the AI Insights tab before generating the report.'}"
    
    html += """
            </div>
        </div>
        
        <div style="text-align: center; color: #95a5a6; font-size: 0.9em; margin-top: 50px;">
            <p>Generated by DataWhisper | Powered by AI & Pandas</p>
        </div>
    </body>
    </html>
    """
    
    return html
