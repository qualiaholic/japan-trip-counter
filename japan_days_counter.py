import csv
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.dates import DateFormatter, DayLocator

CSV_FILE = "filename.csv"
MAX_DAYS = 180  # Maximum allowed days in Japan per 365-day window

def load_trips(csv_file):
    trips = []
    with open(csv_file, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            entry = datetime.strptime(row['entry'], "%Y-%m-%d").date()
            exit = datetime.strptime(row['exit'], "%Y-%m-%d").date()
            trips.append((entry, exit))
    return trips

def days_in_rolling_window(trips, reference_date=None):
    if reference_date is None:
        reference_date = datetime.today().date()
    start_window = reference_date - timedelta(days=365)
    days_count = 0

    for entry, exit in trips:
        # Ignore trips completely outside the rolling window
        if exit < start_window or entry > reference_date:
            continue
        # Count only overlapping days
        overlap_start = max(entry, start_window)
        overlap_end = min(exit, reference_date)
        days_count += (overlap_end - overlap_start).days + 1

    return days_count, start_window

def create_visualization(trips, reference_date=None):
    if reference_date is None:
        reference_date = datetime.today().date()
    
    # Calculate the 365-day rolling window (past 365 days from today)
    days_used, past_window_start = days_in_rolling_window(trips, reference_date)
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), height_ratios=[1, 2])
    
    # Top subplot: Summary statistics
    ax1.axis('off')
    summary_text = f"""
    Total Days Spent in Japan (Last 365 Days): {days_used} days
    365-Day Rolling Window Start: {past_window_start.strftime('%Y-%m-%d')}
    Today's Date: {reference_date.strftime('%Y-%m-%d')}
    Days Remaining Before 180-Day Limit: {MAX_DAYS - days_used} days
    """
    ax1.text(0.5, 0.5, summary_text, fontsize=14, ha='center', va='center',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
             family='monospace')
    
    # Bottom subplot: Timeline visualization
    # Find the earliest and latest dates for the timeline
    all_dates = [trip[0] for trip in trips] + [trip[1] for trip in trips]
    earliest_date = min(min(all_dates), past_window_start)
    latest_date = max(max(all_dates), reference_date)
    
    # Add some padding
    date_range = (latest_date - earliest_date).days
    padding = max(30, date_range * 0.1)
    timeline_start = earliest_date - timedelta(days=int(padding))
    timeline_end = latest_date + timedelta(days=int(padding))
    
    # Convert dates to datetime for plotting
    timeline_start_dt = datetime.combine(timeline_start, datetime.min.time())
    timeline_end_dt = datetime.combine(timeline_end, datetime.min.time())
    reference_date_dt = datetime.combine(reference_date, datetime.min.time())
    past_window_start_dt = datetime.combine(past_window_start, datetime.min.time())
    
    # Draw the 365-day rolling window
    ax2.axvspan(past_window_start_dt, reference_date_dt, alpha=0.3, color='lightblue',
                label='365-Day Rolling Window')
    
    # Draw vertical line for today
    ax2.axvline(reference_date_dt, color='red', linestyle='--', linewidth=2,
                label=f"Today ({reference_date.strftime('%Y-%m-%d')})")
    
    # Draw vertical line for window start
    ax2.axvline(past_window_start_dt, color='blue', linestyle='--', linewidth=2,
                label=f"Window Start ({past_window_start.strftime('%Y-%m-%d')})")
    
    # Plot each trip
    y_positions = []
    for i, (entry, exit_date) in enumerate(trips):
        entry_dt = datetime.combine(entry, datetime.min.time())
        exit_dt = datetime.combine(exit_date, datetime.min.time())
        
        # Calculate y position to avoid overlap
        y_pos = i * 0.3
        
        # Draw trip bar
        trip_duration = (exit_date - entry).days + 1
        # Color trips within the past 365 days as dark green, others as orange
        color = 'darkgreen' if entry >= past_window_start and exit_date <= reference_date else 'orange'
        ax2.barh(y_pos, trip_duration, left=entry_dt, height=0.2, 
                color=color, alpha=0.7, edgecolor='black', linewidth=1)
        
        # Add trip label
        mid_date = entry + timedelta(days=trip_duration // 2)
        ax2.text(datetime.combine(mid_date, datetime.min.time()), y_pos,
                f"{entry.strftime('%Y-%m-%d')} to {exit_date.strftime('%Y-%m-%d')}\n({trip_duration} days)",
                ha='center', va='center', fontsize=8, bbox=dict(boxstyle='round,pad=0.3',
                facecolor='white', alpha=0.8))
        
        y_positions.append(y_pos)
    
    # Set labels and title
    ax2.set_xlim(timeline_start_dt, timeline_end_dt)
    ax2.set_ylim(-0.5, max(y_positions) + 0.5 if y_positions else 1)
    ax2.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax2.set_ylabel('')  # Y-axis is just for visual separation, no meaningful values
    ax2.set_yticks([])  # Hide y-axis ticks since they don't represent meaningful data
    ax2.set_title('Japan Trip Timeline - 365-Day Rolling Window Visualization', 
                  fontsize=14, fontweight='bold', pad=20)
    ax2.grid(True, alpha=0.3, linestyle='--', axis='x')  # Only show horizontal grid lines
    ax2.legend(loc='upper left', fontsize=9)
    
    # Format x-axis dates
    ax2.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    ax2.xaxis.set_major_locator(DayLocator(interval=max(1, date_range // 10)))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig('japan_trips_visualization.png', dpi=300, bbox_inches='tight')
    print(f"\nVisualization saved as 'japan_trips_visualization.png'")
    plt.show()

def main():
    trips = load_trips(CSV_FILE)
    days_used, start_window = days_in_rolling_window(trips)
    days_remaining = MAX_DAYS - days_used
    reference_date = datetime.today().date()

    print(f"Days spent in Japan in the last 365 days: {days_used}")
    print(f"Days remaining before hitting ~180 days: {days_remaining}")
    print(f"\n365-Day Rolling Window Information:")
    print(f"  Window Start Date: {start_window.strftime('%Y-%m-%d')}")
    print(f"  Today's Date: {reference_date.strftime('%Y-%m-%d')}")
    
    # Create visualization
    create_visualization(trips, reference_date)

if __name__ == "__main__":
    main()
