import org.junit.jupiter.api.*;
import org.openqa.selenium.*;
import org.openqa.selenium.chrome.*;
import org.openqa.selenium.support.ui.*;
import java.io.File;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.time.Duration;

public class YoutubeNavigateSubscriptionsThenMoviesTest {

    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeEach
    public void setUp() {
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--headless=new");
        options.addArguments("--no-sandbox");
        options.addArguments("--disable-dev-shm-usage");
        options.addArguments("--window-size=1920,1080");
        options.addArguments("--disable-gpu");
        options.addArguments("--lang=en-US");
        driver = new ChromeDriver(options);
        wait = new WebDriverWait(driver, Duration.ofSeconds(20));
    }

    @AfterEach
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    private void captureScreenshot(String name) {
        try {
            File src = ((TakesScreenshot) driver).getScreenshotAs(OutputType.FILE);
            Files.copy(src.toPath(), Paths.get(name + ".png"));
        } catch (Exception ignored) {
        }
    }

    private WebElement clickSideNavItem(String label) {
        String xpath = "//tp-yt-paper-item[.//yt-formatted-string[normalize-space(text())='" + label + "'] or normalize-space(.)='" + label + "']";
        WebElement item = wait.until(ExpectedConditions.elementToBeClickable(By.xpath(xpath)));
        item.click();
        return item;
    }

    @Test
    public void testNavigateSubscriptionsThenMovies() {
        try {
            // Step 1: navigate to YouTube
            driver.get("https://www.youtube.com/");
            wait.until(ExpectedConditions.titleContains("YouTube"));
            Assertions.assertTrue(driver.getCurrentUrl().contains("youtube.com"),
                    "Expected to be on youtube.com");

            // Step 2: click Subscriptions in the side nav
            clickSideNavItem("Subscriptions");
            wait.until(ExpectedConditions.urlContains("/feed/subscriptions"));
            wait.until(ExpectedConditions.titleContains("Subscriptions"));
            Assertions.assertTrue(driver.getCurrentUrl().contains("/feed/subscriptions"),
                    "URL should contain /feed/subscriptions");
            Assertions.assertTrue(driver.getTitle().contains("Subscriptions"),
                    "Title should contain Subscriptions");

            // Step 3: click Movies in the side nav
            clickSideNavItem("Movies");
            wait.until(ExpectedConditions.or(
                    ExpectedConditions.urlContains("/feed/storefront"),
                    ExpectedConditions.urlContains("/movies"),
                    ExpectedConditions.titleContains("Movies")
            ));
            String finalUrl = driver.getCurrentUrl();
            String finalTitle = driver.getTitle();
            Assertions.assertTrue(
                    finalUrl.contains("/feed/storefront") || finalUrl.contains("/movies") || finalTitle.contains("Movies"),
                    "Expected to land on the Movies destination, got url=" + finalUrl + " title=" + finalTitle);
        } catch (Exception e) {
            captureScreenshot("youtube_navigate_subscriptions_then_movies_failure");
            Assertions.fail("Test failed: " + e.getMessage());
        }
    }
}