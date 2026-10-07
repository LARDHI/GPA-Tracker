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
}