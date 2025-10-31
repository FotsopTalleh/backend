import pdfplumber
import pandas as pd
import re
from typing import List, Dict, Any

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    return ' '.join(str(text).strip().split())

def normalize_time(time_str: str) -> str:
    """Normalize time format to HH:MM-HH:MM"""
    if not time_str:
        return ""
    
    # Remove extra spaces and convert to string
    time_str = str(time_str).strip()
    
    # Handle various time formats
    patterns = [
        r'(\d{1,2}):?(\d{2})?\s*[-–—]\s*(\d{1,2}):?(\d{2})?',  # 7:00-9:00, 7-9, etc.
        r'(\d{1,2})\s*[-–—]\s*(\d{1,2})',  # 7 - 9
    ]
    
    for pattern in patterns:
        match = re.search(pattern, time_str)
        if match:
            groups = match.groups()
            if len(groups) >= 2:
                start_hour = groups[0].zfill(2)
                end_hour = groups[2] if len(groups) > 2 else groups[1]
                end_hour = end_hour.zfill(2)
                
                # Add :00 for minutes if not present
                start_time = f"{start_hour}:00" if ':' not in time_str else f"{start_hour}:{groups[1] or '00'}"
                end_time = f"{end_hour}:00" if ':' not in time_str else f"{end_hour}:{groups[3] or '00'}"
                
                return f"{start_time}-{end_time}"
    
    return time_str

def normalize_day(day_str: str) -> str:
    """Normalize day names"""
    if not day_str:
        return ""
    
    day_str = str(day_str).strip().lower()
    
    day_mapping = {
        'mon': 'Monday',
        'monday': 'Monday',
        'tue': 'Tuesday',
        'tues': 'Tuesday',
        'tuesday': 'Tuesday',
        'wed': 'Wednesday',
        'wednesday': 'Wednesday',
        'thu': 'Thursday',
        'thur': 'Thursday',
        'thurs': 'Thursday',
        'thursday': 'Thursday',
        'fri': 'Friday',
        'friday': 'Friday',
        'sat': 'Saturday',
        'saturday': 'Saturday'
    }
    
    return day_mapping.get(day_str, day_str.title())

def extract_table_from_pdf(pdf_path: str) -> List[List[str]]:
    """Extract tables from PDF using pdfplumber"""
    tables = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extract tables from the page
            page_tables = page.extract_tables()
            if page_tables:
                for table in page_tables:
                    # Clean the table data
                    cleaned_table = []
                    for row in table:
                        cleaned_row = [clean_text(cell) for cell in row] if row else []
                        if any(cleaned_row):  # Only add non-empty rows
                            cleaned_table.append(cleaned_row)
                    if cleaned_table:
                        tables.extend(cleaned_table)
    
    return tables

def parse_faculty_timetable(pdf_path: str) -> List[Dict[str, str]]:
    """Parse faculty timetable PDF"""
    tables = extract_table_from_pdf(pdf_path)
    courses = []
    
    for row in tables:
        if len(row) >= 6:  # Assuming we have at least 6 columns
            course = {
                'course_code': clean_text(row[0]),
                'course_title': clean_text(row[1]),
                'day': normalize_day(row[2]),
                'time': normalize_time(row[3]),
                'hall': clean_text(row[4]),
                'lecturer': clean_text(row[5]) if len(row) > 5 else ''
            }
            
            # Only add valid courses (with code, day, and time)
            if course['course_code'] and course['day'] and course['time']:
                courses.append(course)
    
    return courses

def parse_form_b(pdf_path: str) -> List[Dict[str, str]]:
    """Parse Form B PDF to get student's courses"""
    tables = extract_table_from_pdf(pdf_path)
    student_courses = []
    
    for row in tables:
        if len(row) >= 3:  # Assuming we have at least course code, title, and status
            course = {
                'course_code': clean_text(row[0]),
                'course_title': clean_text(row[1]),
                'status': clean_text(row[2]) if len(row) > 2 else ''
            }
            
            if course['course_code']:
                student_courses.append(course)
    
    return student_courses

def parse_pdfs_and_generate_timetable(faculty_pdf_path: str, formb_pdf_path: str) -> Dict[str, Any]:
    """Main function to parse both PDFs and generate timetable"""
    try:
        # Parse both PDFs
        faculty_courses = parse_faculty_timetable(faculty_pdf_path)
        student_courses = parse_form_b(formb_pdf_path)
        
        # Get student's course codes
        student_course_codes = {course['course_code'] for course in student_courses}
        
        # Filter faculty courses to only include student's courses
        filtered_courses = [
            course for course in faculty_courses 
            if course['course_code'] in student_course_codes
        ]
        
        # Generate timetable grid
        timetable = generate_timetable_grid(filtered_courses)
        
        return {
            "timetable": timetable,
            "student_courses": student_courses,
            "filtered_courses": filtered_courses
        }
        
    except Exception as e:
        raise Exception(f"Error parsing PDFs: {str(e)}")

def generate_timetable_grid(courses: List[Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    """Generate the 7x7 timetable grid"""
    slots = [
        "07:00-09:00", "09:00-11:00", "11:00-13:00",
        "13:00-15:00", "15:00-17:00", "17:00-19:00"
    ]
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    
    # Initialize empty timetable
    timetable = {day: {slot: "" for slot in slots} for day in days}
    
    # Populate timetable
    for course in courses:
        day = course['day']
        time = course['time']
        code = course['course_code']
        title = course['course_title']
        hall = course['hall']
        
        # Check if this day and time slot exists in our grid
        if day in timetable and time in timetable[day]:
            course_info = f"{code}\n{title}\n{hall}"
            
            if timetable[day][time]:
                timetable[day][time] += f"\n---\n{course_info}"
            else:
                timetable[day][time] = course_info
    
    return timetable