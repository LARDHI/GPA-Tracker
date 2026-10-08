public class Course {

    String courseName;
    String courseCode;
    float creditHours;
    String grade;

    public Course(
            String courseName,
            String courseCode,
            float creditHours,
            String grade) {

        this.courseName = courseName;
        this.courseCode = courseCode;
        this.creditHours = creditHours;
        this.grade = grade;
    }
}