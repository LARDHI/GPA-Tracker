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
        testCGPAAcrossMultipleSemesters();
        testCGPAWithNoSemesters();
        testProgramAcceptsMultipleSemesters();
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

    private static void testCGPAAcrossMultipleSemesters() {
        GPACalculator calculator = new GPACalculator();
        ArrayList<Semester> semesters = new ArrayList<>();

        Semester fall = new Semester();
        fall.semesterName = "Fall 2026";
        fall.courses = new ArrayList<>();
        fall.courses.add(new Course("Course A", "A101", 3, "A+"));
        fall.courses.add(new Course("Course B", "B101", 2, "B"));

        Semester spring = new Semester();
        spring.semesterName = "Spring 2027";
        spring.courses = new ArrayList<>();
        spring.courses.add(new Course("Course C", "C101", 1, "A"));

        semesters.add(fall);
        semesters.add(spring);

        assertEquals(21.75, calculator.totalAcademicQualityPoints(
                4.0f, "Plus Only", semesters),
                "Multiple semesters total quality points");
        assertEquals(6.0, calculator.totalAcademicCreditHours(semesters),
                "Multiple semesters total credit hours");
        assertEquals(3.625, calculator.cgpa(
                4.0f, "Plus Only", semesters),
                "CGPA must be weighted by credit hours");

        assertTrue(calculator.bestSemester(4.0f, "Plus Only", semesters) == spring,
                "Best semester should have the highest semester GPA");
        assertTrue(calculator.lowestSemester(4.0f, "Plus Only", semesters) == fall,
                "Lowest semester should have the lowest semester GPA");
    }

    private static void testCGPAWithNoSemesters() {
        GPACalculator calculator = new GPACalculator();
        ArrayList<Semester> semesters = new ArrayList<>();

        assertTrue(Double.isNaN(calculator.cgpa(
                4.0f, "Plus Only", semesters)),
                "CGPA with no semesters should be undefined");
        assertEquals(0.0, calculator.totalAcademicQualityPoints(
                4.0f, "Plus Only", semesters),
                "No semesters should have zero quality points");
        assertEquals(0.0, calculator.totalAcademicCreditHours(semesters),
                "No semesters should have zero credit hours");
        assertTrue(calculator.bestSemester(4.0f, "Plus Only", semesters) == null,
                "Best semester should be null when there are no semesters");
        assertTrue(calculator.lowestSemester(4.0f, "Plus Only", semesters) == null,
                "Lowest semester should be null when there are no semesters");
    }

    private static void testProgramAcceptsMultipleSemesters() throws Exception {
        String input = String.join("\n",
                "Multi Semester Student",
                "1",
                "1",
                "Fall 2026",
                "1",
                "Course A",
                "A101",
                "3",
                "A+",
                "maybe",
                "Y",
                "Spring 2027",
                "1",
                "Course B",
                "B101",
                "2",
                "B",
                "N",
                "");

        InputStream originalIn = System.in;
        PrintStream originalOut = System.out;
        ByteArrayOutputStream output = new ByteArrayOutputStream();

        try {
            System.setIn(new ByteArrayInputStream(input.getBytes(StandardCharsets.UTF_8)));
            System.setOut(new PrintStream(output, true, "UTF-8"));
            Program.main(new String[0]);
        } finally {
            System.setIn(originalIn);
            System.setOut(originalOut);
        }

        String result = output.toString("UTF-8");
        assertTrue(result.contains("Invalid choice. Enter Y or N."),
                "Program must validate the add-semester choice");
        assertTrue(result.contains("Semester Name       : Fall 2026"),
                "Program must keep the first semester");
        assertTrue(result.contains("Semester Name       : Spring 2027"),
                "Program must accept a second semester");
        assertTrue(result.contains("Semester GPA        : 4.0"),
                "First semester GPA must match its own courses");
        assertTrue(result.contains("Semester GPA        : 3.0"),
                "Second semester GPA must match its own courses");
        assertTrue(result.indexOf("Semester Name       : Fall 2026")
                        < result.indexOf("Semester Name       : Spring 2027"),
                "Semester summaries must be displayed in entry order");
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
                "N",
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
