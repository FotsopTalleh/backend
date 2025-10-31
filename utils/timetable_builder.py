from weasyprint import HTML
import tempfile
import os

def generate_html_template(timetable_data: dict) -> str:
    """Generate HTML for the timetable"""
    slots = [
        "07:00-09:00", "09:00-11:00", "11:00-13:00",
        "13:00-15:00", "15:00-17:00", "17:00-19:00"
    ]
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Personalized Timetable</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .timetable { border-collapse: collapse; width: 100%; }
            .timetable th, .timetable td { 
                border: 1px solid #ddd; 
                padding: 12px; 
                text-align: center;
                vertical-align: top;
            }
            .timetable th { 
                background-color: #4CAF50; 
                color: white; 
                font-weight: bold;
            }
            .timetable tr:nth-child(even) { background-color: #f2f2f2; }
            .time-slot { font-weight: bold; color: #333; }
            .course-info { font-size: 12px; margin: 5px 0; }
            .course-code { font-weight: bold; color: #2c3e50; }
            .course-title { color: #34495e; }
            .course-hall { color: #7f8c8d; font-style: italic; }
            .separator { border-top: 1px dashed #bdc3c7; margin: 8px 0; }
        </style>
    </head>
    <body>
        <h1>Personalized Timetable</h1>
        <table class="timetable">
            <thead>
                <tr>
                    <th>Time/Day</th>
    """
    
    # Add day headers
    for day in days:
        html += f'<th>{day}</th>'
    html += '</tr></thead><tbody>'
    
    # Add time slots and data
    for slot in slots:
        html += f'<tr><td class="time-slot">{slot}</td>'
        for day in days:
            cell_content = timetable_data.get(day, {}).get(slot, '')
            if cell_content:
                # Format the cell content
                courses = cell_content.split('\n---\n')
                course_html = ''
                for i, course in enumerate(courses):
                    if i > 0:
                        course_html += '<div class="separator"></div>'
                    parts = course.split('\n')
                    if len(parts) >= 3:
                        course_html += f'''
                        <div class="course-info">
                            <div class="course-code">{parts[0]}</div>
                            <div class="course-title">{parts[1]}</div>
                            <div class="course-hall">{parts[2]}</div>
                        </div>
                        '''
                html += f'<td>{course_html}</td>'
            else:
                html += '<td></td>'
        html += '</tr>'
    
    html += '</tbody></table></body></html>'
    return html

def generate_pdf(timetable_data: dict) -> str:
    """Generate PDF from timetable data"""
    try:
        # Generate HTML
        html_content = generate_html_template(timetable_data)
        
        # Create temporary file for PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            pdf_path = temp_file.name
        
        # Generate PDF
        HTML(string=html_content).write_pdf(pdf_path)
        
        return pdf_path
        
    except Exception as e:
        raise Exception(f"Error generating PDF: {str(e)}")