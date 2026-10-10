import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;

public class GPACalculatorTest {

    private static int testsPassed = 0;

    public static void main(String[] args) throws Exception {
        testFourPointPlusOnly();
        testFivePointPlusOnly();
        testFourPointPlusMinus();
        testFivePointPlusMinus();
        testInvalidGrade();
        testEmptySemester();
        testProgramDisplaysMatchingResults();

        System.out.println("All " + testsPassed + " GPA tests passed.");
    }

    private static void testFourPointPlusOnly() {
        GPACalculator calculator = new GPACalculator();
        ArrayList<Course> courses = new ArrayList<>();
        courses.add(new Course("Course A", "A101", 3, "A+"));
        courses.add(new Course("Course B", "B101", 2, "B"));

        assertEquals(18.0, calculator.semesterTotalQualityPoints(
                4.0f, "Plus Only", courses), "4.0 Plus Only quality points");
        assertEquals(3.6, calculator.semesterGPA(
                4.0f, "Plus Only", courses), "4.0 Plus Only semester GPA");
    }

    private static void testFivePointPlusOnly() {
        GPACalculator calculator = new GPACalculator();
        ArrayList<Course> courses = new ArrayList<>();
        courses.add(new Course("Course A", "A101", 3, "A+"));
        courses.add(new Course("Course B", "B101", 2, "B"));

        assertEquals(23.0, calculator.semesterTotalQualityPoints(
                5.0f, "Plus Only", courses), "5.0 Plus Only quality points");
        assertEquals(4.6, calculator.semesterGPA(
                5.0f, "Plus Only", courses), "5.0 Plus Only semester GPA");
    }

    private static void testFourPointPlusMinus() {
        GPACalculator calculator = new GPACalculator();
        ArrayList<Course> courses = new ArrayList<>();
        courses.add(new Course("Course A", "A101", 3, "A-"));
        courses.add(new Course("Course B", "B101", 2, "B+"));

        assertEquals(17.67, calculator.semesterTotalQualityPoints(
                4.0f, "Plus / Minus", courses), "4.0 Plus / Minus quality points");
        assertEquals(3.534, calculator.semesterGPA(
                4.0f, "Plus / Minus", courses), "4.0 Plus / Minus semester GPA");
    }

    private static void testFivePointPlusMinus() {
        GPACalculator calculator = new GPACalculator();
        ArrayList<Course> courses = new ArrayList<>();
        courses.add(new Course("Course A", "A101", 3, "A-"));
        courses.add(new Course("Course B", "B101", 2, "B+"));

        assertEquals(22.0, calculator.semesterTotalQualityPoints(
                5.0f, "Plus / Minus", courses), "5.0 Plus / Minus quality points");
        assertEquals(4.4, calculator.semesterGPA(
                5.0f, "Plus / Minus", courses), "5.0 Plus / Minus semester GPA");
    }

    private static void testInvalidGrade() {
        GPACalculator calculator = new GPACalculator();
        boolean threwExpectedException = false;

        try {
            calculator.gradeToGradePoint("Z", 4.0f, "Plus Only");
        } catch (IllegalArgumentException exception) {
            threwExpectedException = true;
        }

        assertTrue(threwExpectedException, "Invalid grades must be rejected");
    }

    private static void testEmptySemester() {
        GPACalculator calculator = new GPACalculator();
        ArrayList<Course> courses = new ArrayList<>();

        assertTrue(Double.isNaN(calculator.semesterGPA(
                4.0f, "Plus Only", courses)), "An empty semester must not have a GPA");
        assertEquals(0.0, calculator.semesterTotalQualityPoints(
                4.0f, "Plus Only", courses), "Empty semester quality points");
    }

    private static void testProgramDisplaysMatchingResults() throws Exception {
        String input = String.join("\n",
                "Test Student",
                "1",
                "1",
                "Fall 2026",
                "2",
                "Course A",
                "A101",
                "3",
                "A+",
                "Course B",
                "B101",
                "2",
                "B",
                "");

        InputStream originalIn = System.in;
        PrintStream originalOut = System.out;
        ByteArrayOutputStream output = new ByteArrayOutputStream();

        try {
            System.setIn(new ByteArrayInputStream(
                    input.getBytes(StandardCharsets.UTF_8)));
            System.setOut(new PrintStream(output, true, "UTF-8"));

            Program.main(new String[0]);
        } finally {
            System.setIn(originalIn);
            System.setOut(originalOut);
        }

        String result = output.toString("UTF-8");
        assertTrue(result.contains("Semester GPA        : 3.6"),
                "Program must display the expected semester GPA");
        assertTrue(result.contains("Total Credit Hours  : 5.0"),
                "Program must display the expected total credit hours");
        assertTrue(result.contains("Total Quality Points: 18.0"),
                "Program must display the expected total quality points");
    }

    private static void assertEquals(double expected, double actual, String testName) {
        if (Math.abs(expected - actual) > 0.000001) {
            throw new AssertionError(testName + ": expected " + expected
                    + " but got " + actual);
        }
        testsPassed++;
        System.out.println("PASS: " + testName);
    }

    private static void assertTrue(boolean condition, String testName) {
        if (!condition) {
            throw new AssertionError(testName);
        }
        testsPassed++;
        System.out.println("PASS: " + testName);
    }
}
