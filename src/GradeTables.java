import java.util.LinkedHashMap;
import java.util.Map;

public class GradeTables {

    public Map<String, Double> fourPlusOnly() {
        Map<String, Double> gradeTable = new LinkedHashMap<>();

        gradeTable.put("A+", 4.00);
        gradeTable.put("A", 3.75);
        gradeTable.put("B+", 3.50);
        gradeTable.put("B", 3.00);
        gradeTable.put("C+", 2.50);
        gradeTable.put("C", 2.00);
        gradeTable.put("D+", 1.50);
        gradeTable.put("D", 1.00);
        gradeTable.put("F", 0.00);

        return gradeTable;
    }

    public Map<String, Double> fourPlusMinus() {
        Map<String, Double> gradeTable = new LinkedHashMap<>();

        gradeTable.put("A+", 4.00);
        gradeTable.put("A", 3.75);
        gradeTable.put("A-", 3.67);
        gradeTable.put("B+", 3.33);
        gradeTable.put("B", 3.00);
        gradeTable.put("B-", 2.67);
        gradeTable.put("C+", 2.33);
        gradeTable.put("C", 2.00);
        gradeTable.put("C-", 1.67);
        gradeTable.put("D+", 1.33);
        gradeTable.put("D", 1.00);
        gradeTable.put("D-", 0.67);
        gradeTable.put("F", 0.00);

        return gradeTable;
    }

    public Map<String, Double> fivePlusOnly() {
        Map<String, Double> gradeTable = new LinkedHashMap<>();

        gradeTable.put("A+", 5.00);
        gradeTable.put("A", 4.75);
        gradeTable.put("B+", 4.50);
        gradeTable.put("B", 4.00);
        gradeTable.put("C+", 3.50);
        gradeTable.put("C", 3.00);
        gradeTable.put("D+", 2.50);
        gradeTable.put("D", 2.00);
        gradeTable.put("F", 1.00);

        return gradeTable;
    }

    public Map<String, Double> fivePlusMinus() {
        Map<String, Double> gradeTable = new LinkedHashMap<>();

        gradeTable.put("A+", 5.00);
        gradeTable.put("A", 4.75);
        gradeTable.put("A-", 4.50);
        gradeTable.put("B+", 4.25);
        gradeTable.put("B", 4.00);
        gradeTable.put("B-", 3.75);
        gradeTable.put("C+", 3.50);
        gradeTable.put("C", 3.00);
        gradeTable.put("C-", 2.75);
        gradeTable.put("D+", 2.50);
        gradeTable.put("D", 2.00);
        gradeTable.put("D-", 1.75);
        gradeTable.put("F", 1.00);

        return gradeTable;
    }

    public boolean isValidGrade(
            String grade,
            float gpaScale,
            String gradingSystem) {

        Map<String, Double> gradeTable;

        if (gpaScale == 4.0) {
            if (gradingSystem.equals("Plus Only")) {
                gradeTable = fourPlusOnly();
            } else {
                gradeTable = fourPlusMinus();
            }
        } else {
            if (gradingSystem.equals("Plus Only")) {
                gradeTable = fivePlusOnly();
            } else {
                gradeTable = fivePlusMinus();
            }
        }

        return gradeTable.containsKey(grade);
    }

    public String validGrades(
            float gpaScale,
            String gradingSystem) {

        Map<String, Double> gradeTable;

        if (gpaScale == 4.0) {
            if (gradingSystem.equals("Plus Only")) {
                gradeTable = fourPlusOnly();
            } else {
                gradeTable = fourPlusMinus();
            }
        } else {
            if (gradingSystem.equals("Plus Only")) {
                gradeTable = fivePlusOnly();
            } else {
                gradeTable = fivePlusMinus();
            }
        }

        return String.join(", ", gradeTable.keySet());
    }
}