import java.util.Scanner;
import java.util.ArrayList;

class Program {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        String fullName;
        while (true) {

            System.out.print("Enter your Full Name: ");
            fullName = sc.nextLine();

            String[] names = fullName.trim().split("\\s+");

            if (names.length == 4) {
                break;
            }
        }

        float gpaScale;

        while (true) {
            System.out.println("Select GPA Scale:");
            System.out.println("1. 4.0");
            System.out.println("2. 5.0");

            int choice = sc.nextInt();

            if (choice == 1) {
                gpaScale = 4.0f;
                break;
            }
            else if (choice == 2) {
                gpaScale = 5.0f;
                break;
            }
        }

        String gradingSystem;

        while (true) {
            System.out.println("Select Grading System:");
            System.out.println("1. Plus Only");
            System.out.println("2. Plus / Minus");

            int choice = sc.nextInt();

            if (choice == 1) {
                gradingSystem = "Plus Only";
                break;
            }
            else if (choice == 2) {
                gradingSystem = "Plus / Minus";
                break;
            }
        }

        Student student = new Student(
                fullName,
                gpaScale,
                gradingSystem
        );

        sc.nextLine();

        String semesterName;

        while (true) {
            System.out.print("Enter Semester Name: ");
            semesterName = sc.nextLine();

            if (semesterName.trim().isEmpty()) {
                continue;
            }

            boolean exist = false;

            for (Semester semester : student.semesters) {
                if (semester.semesterName.equals(semesterName)) {
                    exist = true;
                    break;
                }
            }

            if (exist) {
                System.out.println("Semester already exists.");
                continue;
            }

            break;
        }

        Semester semester = new Semester();
        semester.semesterName = semesterName;
        semester.courses = new ArrayList<>();

        student.semesters.add(semester);

        GradeTables gradeTables = new GradeTables();

        int coursesNumber;

        while (true) {
            System.out.print("Enter Number of Courses: ");
            coursesNumber = sc.nextInt();

            if (coursesNumber <= 0) {
                System.out.println("Enter Valid Number");
                continue;
            }

            break;
        }

        sc.nextLine();

        String courseName;
        String courseCode;
        float creditHours;
        String grade;

        for (int i = 0; i < coursesNumber; i++) {

            System.out.print("Enter Course Name: ");
            courseName = sc.nextLine();

            System.out.print("Enter Course Code: ");
            courseCode = sc.nextLine();

            System.out.print("Enter Credit Hours: ");
            creditHours = sc.nextFloat();
            sc.nextLine();

            while (true) {
                System.out.print("Enter Grade: ");
                grade = sc.nextLine();

                if (!gradeTables.isValidGrade(
                        grade,
                        gpaScale,
                        gradingSystem)) {

                    System.out.println(
                            "Valid grades: " +
                            gradeTables.validGrades(
                                    gpaScale,
                                    gradingSystem
                            )
                    );

                    continue;
                }

                break;
            }

            Course course = new Course(
                    courseName,
                    courseCode,
                    creditHours,
                    grade
            );

            semester.courses.add(course);
        }
        sc.close();
    }
}