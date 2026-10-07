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
}