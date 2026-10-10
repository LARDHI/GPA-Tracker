import java.util.Scanner;
import java.util.ArrayList;

class Program {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        String fullName;
        while (true) {
            System.out.print("Enter your Full Name: ");
            fullName = sc.nextLine().trim().replaceAll("\\s+", " ");

            if (!fullName.isEmpty()) {
                break;
            }

            System.out.println("Name can't be empty.");
        }

        float gpaScale;
        while (true) {
            System.out.println("Select GPA Scale:");
            System.out.println("1. 4.0");
            System.out.println("2. 5.0");

            if (sc.hasNextInt()) {
                int choice = sc.nextInt();

                if (choice == 1) {
                    gpaScale = 4.0f;
                    break;
                } else if (choice == 2) {
                    gpaScale = 5.0f;
                    break;
                } else {
                    System.out.println("Enter 1 or 2");
                }
            } else {
                System.out.println("Invalid Input");
                sc.nextLine();
            }
        }

        String gradingSystem;
        while (true) {
            System.out.println("Select Grading System:");
            System.out.println("1. Plus Only");
            System.out.println("2. Plus / Minus");

            if (sc.hasNextInt()) {
                int choice = sc.nextInt();

                if (choice == 1) {
                    gradingSystem = "Plus Only";
                    break;
                } else if (choice == 2) {
                    gradingSystem = "Plus / Minus";
                    break;
                } else {
                    System.out.println("Enter 1 or 2");
                }
            } else {
                System.out.println("Invalid Input");
                sc.nextLine();
            }
        }

        Student student = new Student(fullName, gpaScale, gradingSystem);
        sc.nextLine();

        GradeTables gradeTables = new GradeTables();
        GPACalculator gpaCalculator = new GPACalculator();
        String addAnotherSemester;

        do {
            String semesterName;
            while (true) {
                System.out.print("Enter Semester Name: ");
                semesterName = sc.nextLine().trim();

                if (semesterName.isEmpty()) {
                    System.out.println("Semester name can't be empty.");
                    continue;
                }

                boolean exists = false;
                for (Semester existingSemester : student.semesters) {
                    if (existingSemester.semesterName.equalsIgnoreCase(semesterName)) {
                        exists = true;
                        break;
                    }
                }

                if (exists) {
                    System.out.println("Semester already exists.");
                    continue;
                }

                break;
            }

            Semester semester = new Semester();
            semester.semesterName = semesterName;
            semester.courses = new ArrayList<>();
            student.semesters.add(semester);

            int coursesNumber;
            while (true) {
                System.out.print("Enter Number of Courses: ");

                if (sc.hasNextInt()) {
                    coursesNumber = sc.nextInt();

                    if (coursesNumber <= 0) {
                        System.out.println("Enter Valid Number");
                        continue;
                    }
                    break;
                } else {
                    System.out.println("Invalid Input");
                    sc.nextLine();
                }
            }
            sc.nextLine();

            for (int i = 0; i < coursesNumber; i++) {
                String courseName;
                while (true) {
                    System.out.print("Enter Course Name: ");
                    courseName = sc.nextLine().trim();

                    if (courseName.isEmpty()) {
                        System.out.println("You can't Enter Empty Name");
                        continue;
                    }
                    break;
                }

                String courseCode;
                while (true) {
                    System.out.print("Enter Course Code: ");
                    courseCode = sc.nextLine().trim();

                    if (courseCode.isEmpty()) {
                        System.out.println("You Can't Enter Empty Code");
                        continue;
                    }
                    break;
                }

                float creditHours;
                while (true) {
                    System.out.print("Enter Credit Hours: ");

                    if (sc.hasNextFloat()) {
                        creditHours = sc.nextFloat();

                        if (creditHours <= 0) {
                            System.out.println("Credit hours must be greater than 0");
                            continue;
                        }
                        break;
                    } else {
                        System.out.println("Invalid Input");
                        sc.nextLine();
                    }
                }
                sc.nextLine();

                String grade;
                while (true) {
                    System.out.print("Enter Grade: ");
                    grade = sc.nextLine().trim().toUpperCase();

                    if (!gradeTables.isValidGrade(grade, gpaScale, gradingSystem)) {
                        System.out.println("Valid grades: "
                                + gradeTables.validGrades(gpaScale, gradingSystem));
                        continue;
                    }

                    break;
                }

                Course course = new Course(courseName, courseCode, creditHours, grade);
                semester.courses.add(course);
            }

            double semesterGPA = gpaCalculator.semesterGPA(
                    student.gpaScale, student.gradingSystem, semester.courses);
            float totalCreditHours = 0;
            for (Course course : semester.courses) {
                totalCreditHours += course.creditHours;
            }

            double totalQualityPoints = gpaCalculator.semesterTotalQualityPoints(
                    student.gpaScale, student.gradingSystem, semester.courses);

            System.out.println("\n========== Semester Summary ==========");
            System.out.println("Semester Name       : " + semester.semesterName);
            System.out.println("Semester GPA        : " + semesterGPA);
            System.out.println("Total Credit Hours  : " + totalCreditHours);
            System.out.println("Total Quality Points: " + totalQualityPoints);
            System.out.println("======================================");

            while (true) {
                System.out.print("Add another semester? (Y/N): ");
                addAnotherSemester = sc.nextLine().trim().toUpperCase();

                if (addAnotherSemester.equals("Y") || addAnotherSemester.equals("N")) {
                    break;
                }

                System.out.println("Invalid choice. Enter Y or N.");
            }
        } while (addAnotherSemester.equals("Y"));

        sc.close();
    }
}
