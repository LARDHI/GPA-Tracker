import java.util.ArrayList;

public class Student {

    String fullName;
    float gpaScale;
    String gradingSystem;
    ArrayList<Semester> semesters;

    public Student(
            String fullName,
            float gpaScale,
            String gradingSystem) {

        this.fullName = fullName;
        this.gpaScale = gpaScale;
        this.gradingSystem = gradingSystem;
        this.semesters = new ArrayList<>();
    }
}