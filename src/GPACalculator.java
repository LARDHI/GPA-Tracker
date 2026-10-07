import java.util.ArrayList;
import java.util.Map;

public class GPACalculator {

    public double gradeToGradePoint(
            String grade,
            float gpaScale,
            String gradingSystem) {

        Map<String, Double> gradeTable;

        GradeTables gradeTables = new GradeTables();

        if (gpaScale == 4.0) {

            if (gradingSystem.equals("Plus Only")) {
                gradeTable = gradeTables.fourPlusOnly();
            } else {
                gradeTable = gradeTables.fourPlusMinus();
            }

        } else {

            if (gradingSystem.equals("Plus Only")) {
                gradeTable = gradeTables.fivePlusOnly();
            } else {
                gradeTable = gradeTables.fivePlusMinus();
            }
        }

        return gradeTable.get(grade);
    }


    public double qualityPoints(
            String grade,
            float gpaScale,
            String gradingSystem,
            float creditHours) {

        double gradePoint = gradeToGradePoint(
                grade,
                gpaScale,
                gradingSystem
        );

        double qualityPoints = creditHours * gradePoint;

        return qualityPoints;
    }

    public double semesterGPA(
        float gpaScale,
        String gradingSystem,
        ArrayList<Course> courses) {

        if (courses.isEmpty()) {
        return Double.NaN;
        }

        double totalQualityPoints = 0;
        float totalCreditHours = 0;

        for (Course course : courses) {

            totalQualityPoints += qualityPoints(
                course.grade,
                gpaScale,
                gradingSystem,
                course.creditHours
            );

            totalCreditHours += course.creditHours;
        }

        double gpaSemester =
                totalQualityPoints / totalCreditHours;

        double roundedGPA =
                Math.round(gpaSemester * 1000.0) / 1000.0;

        return roundedGPA;
    }

    public double semesterTotalQualityPoints(
        float gpaScale,
        String gradingSystem,
        ArrayList<Course> courses) {

        double semesterTotalQualityPoints = 0;

        for (Course course : courses) {

            semesterTotalQualityPoints += qualityPoints(
                    course.grade,
                    gpaScale,
                    gradingSystem,
                    course.creditHours
            );
        }

        return semesterTotalQualityPoints;
    }

    public double totalAcademicQualityPoints(
        float gpaScale,
        String gradingSystem,
        ArrayList<Semester> semesters) {

        double totalAcademicQualityPoints = 0;

        for (Semester semester : semesters) {

            totalAcademicQualityPoints +=
                semesterTotalQualityPoints(
                        gpaScale,
                        gradingSystem,
                        semester.courses
                );
        }

        return totalAcademicQualityPoints;
    }

    public float totalAcademicCreditHours(
        ArrayList<Semester> semesters) {

        float totalAcademicCreditHours = 0;

        for (Semester semester : semesters) {

            for (Course course : semester.courses) {

                totalAcademicCreditHours += course.creditHours;
            }
        }

        return totalAcademicCreditHours;
    }

    public double cgpa(
        float gpaScale,
        String gradingSystem,
        ArrayList<Semester> semesters) {

        double totalQualityPoints =
            totalAcademicQualityPoints(
                    gpaScale,
                    gradingSystem,
                    semesters
            );

        float totalCreditHours =
                totalAcademicCreditHours(semesters);

        if (totalCreditHours == 0) {
            return Double.NaN;
        }

        double cgpa =
                totalQualityPoints / totalCreditHours;

        double roundedCGPA =
                Math.round(cgpa * 1000.0) / 1000.0;

        return roundedCGPA;
    }

    public Semester bestSemester(
        float gpaScale,
        String gradingSystem,
        ArrayList<Semester> semesters) {

        Semester bestSemester = null;

        for (Semester semester : semesters) {

            if (semester.courses.isEmpty()) {
             continue;
            }

            double currentGPA =
                    semesterGPA(
                        gpaScale,
                        gradingSystem,
                        semester.courses
                    );

            if (bestSemester == null) {

                bestSemester = semester;

            } else {

                double bestGPA =
                        semesterGPA(
                            gpaScale,
                            gradingSystem,
                            bestSemester.courses
                        );

                if (currentGPA > bestGPA) {

                    bestSemester = semester;

                } else if (currentGPA == bestGPA) {

                    float currentCreditHours = 0;
                    float bestCreditHours = 0;

                    for (Course course : semester.courses) {
                        currentCreditHours += course.creditHours;
                    }

                    for (Course course : bestSemester.courses) {
                        bestCreditHours += course.creditHours;
                    }

                    if (currentCreditHours > bestCreditHours) {
                        bestSemester = semester;
                    }
                }
            }
        }

        return bestSemester;
    }

    public Semester lowestSemester(
        float gpaScale,
        String gradingSystem,
        ArrayList<Semester> semesters) {

        Semester lowestSemester = null;

        for (Semester semester : semesters) {

            if (semester.courses.isEmpty()) {
                continue;
            }

            double currentGPA =
                    semesterGPA(
                        gpaScale,
                        gradingSystem,
                        semester.courses
                    );

            if (lowestSemester == null) {

                lowestSemester = semester;

            } else {

                double lowestGPA =
                        semesterGPA(
                            gpaScale,
                            gradingSystem,
                            lowestSemester.courses
                        );

                if (currentGPA < lowestGPA) {

                    lowestSemester = semester;

                } else if (currentGPA == lowestGPA) {

                    float currentCreditHours = 0;
                    float lowestCreditHours = 0;

                    for (Course course : semester.courses) {
                    currentCreditHours += course.creditHours;
                    }

                    for (Course course : lowestSemester.courses) {
                        lowestCreditHours += course.creditHours;
                    }

                    if (currentCreditHours > lowestCreditHours) {
                        lowestSemester = semester;
                    }
                }
            }
        }

        return lowestSemester;
    }
}