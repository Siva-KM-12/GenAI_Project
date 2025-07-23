import matplotlib.pyplot as plt
import pandas as pd
import os
from datetime import datetime
import numpy as np

class VisualizationManager:
    def __init__(self, output_dir="../visualizations"):
        self.output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def create_visualization(self, query_result, user_question, sql_query):
        """Create a visualization based on the query result and question type."""
        if not query_result["success"]:
            return self._create_error_visualization(user_question, query_result.get("error", "Unknown error"))
        
        data = query_result["data"]
        columns = query_result["columns"]
        
        if not data:
            return self._create_no_data_visualization(user_question)
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(data, columns=columns)
        
        # Determine visualization type based on question and data
        question_lower = user_question.lower()
        
        try:
            # Single value questions - create a simple display chart
            if len(data) == 1 and len(data[0]) == 1:
                return self._create_single_value_chart(df, user_question, data[0][0])
            
            # Multiple rows - create appropriate chart based on question type
            elif self._should_create_bar_chart(df, question_lower):
                return self._create_bar_chart(df, user_question)
            elif self._should_create_pie_chart(df, question_lower):
                return self._create_pie_chart(df, user_question)
            elif self._should_create_time_series(df, question_lower):
                return self._create_time_series_plot(df, user_question)
            else:
                return self._create_generic_plot(df, user_question)
                
        except Exception as e:
            print(f"Error creating visualization: {e}")
            return self._create_error_visualization(user_question, str(e))
    
    def _create_single_value_chart(self, df, user_question, value):
        """Create a chart for single value results."""
        plt.figure(figsize=(10, 6))
        
        # Determine the type of value and create appropriate visualization
        question_lower = user_question.lower()
        
        if "total sales" in question_lower:
            # Single bar chart for total sales
            plt.bar(['Total Sales'], [value], color='#2E8B57', width=0.5)
            plt.title(f'Total Sales: ${value:,.2f}', fontsize=16, fontweight='bold')
            plt.ylabel('Sales Amount ($)', fontsize=12)
            
        elif "roas" in question_lower or "return on ad spend" in question_lower:
            # Gauge-like visualization for RoAS
            plt.bar(['RoAS'], [value], color='#FF6347', width=0.5)
            plt.title(f'Return on Ad Spend: {value:.2f}%', fontsize=16, fontweight='bold')
            plt.ylabel('RoAS (%)', fontsize=12)
            
        elif "total ad spend" in question_lower:
            plt.bar(['Total Ad Spend'], [value], color='#4169E1', width=0.5)
            plt.title(f'Total Ad Spend: ${value:,.2f}', fontsize=16, fontweight='bold')
            plt.ylabel('Ad Spend ($)', fontsize=12)
            
        elif "total clicks" in question_lower:
            plt.bar(['Total Clicks'], [value], color='#32CD32', width=0.5)
            plt.title(f'Total Clicks: {value:,}', fontsize=16, fontweight='bold')
            plt.ylabel('Number of Clicks', fontsize=12)
            
        elif "count" in question_lower or "how many" in question_lower:
            plt.bar(['Count'], [value], color='#9370DB', width=0.5)
            plt.title(f'Count: {value:,}', fontsize=16, fontweight='bold')
            plt.ylabel('Count', fontsize=12)
            
        elif "conversion rate" in question_lower:
            plt.bar(['Conversion Rate'], [value], color='#FF8C00', width=0.5)
            plt.title(f'Conversion Rate: {value:.2f}%', fontsize=16, fontweight='bold')
            plt.ylabel('Conversion Rate (%)', fontsize=12)
            
        elif "ctr" in question_lower or "click-through rate" in question_lower:
            plt.bar(['Click-Through Rate'], [value], color='#20B2AA', width=0.5)
            plt.title(f'Click-Through Rate: {value:.2f}%', fontsize=16, fontweight='bold')
            plt.ylabel('CTR (%)', fontsize=12)
            
        else:
            # Generic single value chart
            plt.bar(['Result'], [value], color='#708090', width=0.5)
            plt.title(f'Result: {value:,.2f}' if isinstance(value, float) else f'Result: {value:,}', 
                     fontsize=16, fontweight='bold')
            plt.ylabel('Value', fontsize=12)
        
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        filename = f"single_value_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def _should_create_time_series(self, df, question):
        """Check if data is suitable for time series plot."""
        date_columns = [col for col in df.columns if 'date' in col.lower()]
        return len(date_columns) > 0 and len(df) > 1
    
    def _should_create_bar_chart(self, df, question):
        """Check if data is suitable for bar chart."""
        return ("top" in question or "highest" in question or "lowest" in question or 
                "products" in question) and len(df) > 1
    
    def _should_create_pie_chart(self, df, question):
        """Check if data is suitable for pie chart."""
        return ("distribution" in question or "percentage" in question or 
                "eligibility" in question) and len(df) <= 10
    
    def _create_bar_chart(self, df, user_question):
        """Create a bar chart."""
        plt.figure(figsize=(12, 8))
        
        if len(df.columns) >= 2:
            x_col = df.columns[0]
            y_col = df.columns[1]
            
            # Limit to top 10 items for readability
            df_plot = df.head(10)
            
            # Create colorful bars
            colors = plt.cm.Set3(np.linspace(0, 1, len(df_plot)))
            bars = plt.bar(range(len(df_plot)), df_plot[y_col], color=colors)
            
            plt.xlabel(x_col, fontsize=12)
            plt.ylabel(y_col, fontsize=12)
            plt.title(f'{user_question}', fontsize=14, fontweight='bold')
            plt.xticks(range(len(df_plot)), df_plot[x_col], rotation=45, ha='right')
            plt.grid(True, alpha=0.3, axis='y')
            
            # Add value labels on bars
            for bar, value in zip(bars, df_plot[y_col]):
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height,
                        f'{value:.2f}' if isinstance(value, float) else f'{value}',
                        ha='center', va='bottom', fontsize=10)
            
            plt.tight_layout()
            
            filename = f"barchart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return filepath
        
        return None
    
    def _create_pie_chart(self, df, user_question):
        """Create a pie chart."""
        plt.figure(figsize=(10, 8))
        
        if len(df.columns) >= 2:
            labels_col = df.columns[0]
            values_col = df.columns[1]
            
            # Limit to top 8 slices for readability
            df_plot = df.head(8)
            
            # Create pie chart with custom colors
            colors = plt.cm.Set3(np.linspace(0, 1, len(df_plot)))
            wedges, texts, autotexts = plt.pie(df_plot[values_col], 
                                              labels=df_plot[labels_col],
                                              autopct='%1.1f%%',
                                              colors=colors,
                                              startangle=90)
            
            plt.title(f'{user_question}', fontsize=14, fontweight='bold')
            
            # Improve text readability
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            plt.axis('equal')
            
            filename = f"piechart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return filepath
        
        return None
    
    def _create_time_series_plot(self, df, user_question):
        """Create a time series plot."""
        plt.figure(figsize=(12, 6))
        
        date_col = [col for col in df.columns if 'date' in col.lower()][0]
        value_cols = [col for col in df.columns if col != date_col and df[col].dtype in ['int64', 'float64']]
        
        if not value_cols:
            return None
        
        # Convert date column to datetime
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.sort_values(by=date_col)
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        
        for i, col in enumerate(value_cols[:3]):  # Limit to 3 series
            plt.plot(df[date_col], df[col], marker='o', label=col, 
                    color=colors[i % len(colors)], linewidth=2, markersize=6)
        
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Value', fontsize=12)
        plt.title(f'{user_question}', fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        filename = f"timeseries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def _create_generic_plot(self, df, user_question):
        """Create a generic plot for other data types."""
        plt.figure(figsize=(10, 6))
        
        if len(df.columns) >= 2:
            x_col = df.columns[0]
            y_col = df.columns[1]
            
            # Limit data for readability
            df_plot = df.head(15)
            
            if df_plot[y_col].dtype in ['int64', 'float64']:
                # Numeric data - create bar chart
                colors = plt.cm.viridis(np.linspace(0, 1, len(df_plot)))
                plt.bar(range(len(df_plot)), df_plot[y_col], color=colors)
                plt.xticks(range(len(df_plot)), df_plot[x_col], rotation=45, ha='right')
            else:
                # Non-numeric data - create count plot
                value_counts = df_plot[y_col].value_counts()
                colors = plt.cm.Set2(np.linspace(0, 1, len(value_counts)))
                plt.bar(range(len(value_counts)), value_counts.values, color=colors)
                plt.xticks(range(len(value_counts)), value_counts.index, rotation=45, ha='right')
            
            plt.xlabel(x_col, fontsize=12)
            plt.ylabel(y_col, fontsize=12)
            plt.title(f'{user_question}', fontsize=14, fontweight='bold')
            plt.grid(True, alpha=0.3, axis='y')
            plt.tight_layout()
            
            filename = f"generic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return filepath
        
        return None
    
    def _create_no_data_visualization(self, user_question):
        """Create a visualization when no data is found."""
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, 'No Data Found', fontsize=24, ha='center', va='center',
                transform=plt.gca().transAxes, color='gray')
        plt.title(f'{user_question}', fontsize=14, fontweight='bold')
        plt.axis('off')
        
        filename = f"nodata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def _create_error_visualization(self, user_question, error_message):
        """Create a visualization when an error occurs."""
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, f'Error: {error_message}', fontsize=16, ha='center', va='center',
                transform=plt.gca().transAxes, color='red', wrap=True)
        plt.title(f'{user_question}', fontsize=14, fontweight='bold')
        plt.axis('off')
        
        filename = f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath

