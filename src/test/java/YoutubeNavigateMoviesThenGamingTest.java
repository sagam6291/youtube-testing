import org.junit.jupiter.api.*;
import org.openqa.selenium.*;
import org.openqa.selenium.chrome.*;
import org.openqa.selenium.support.ui.*;
import java.io.File;
import java.nio.file.Files;
import java.time.Duration;
import static org.junit.jupiter.api.Assertions.*;

public class YoutubeNavigateMoviesThenGamingTest {
    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeEach
    public void setUp() {
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--headless=new");
        options.addArguments("--no-sandbox");
        options.addArguments("--disable-dev-shm-usage");
        options.addArguments("--window-size=1920,1080");
        driver = new ChromeDriver(options);
        wait = new WebDriverWait(driver, Duration.ofSeconds(20));
    }

    @AfterEach
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    @Test
    public void testNavigateMoviesThenGaming() {
        try {
            driver.get("https://www.youtube.com/");
            wait.until(ExpectedConditions.titleContains("YouTube"));

            By moviesLocator = By.xpath("//tp-yt-paper-item[.//yt-formatted-string[normalize-space(text())='Movies'] or normalize-space(.)='Movies']");
            WebElement movies = wait.until(ExpectedConditions.elementToBeClickable(moviesLocator));
            movies.click();

            wait.until(ExpectedConditions.titleContains("Movies"));
            wait.until(ExpectedConditions.urlContains("/feed/storefront"));
            assertTrue(driver.getTitle().contains("Movies"), "Title should contain Movies");
            assertTrue(driver.getCurrentUrl().contains("/feed/storefront"), "URL should contain /feed/storefront");

            By gamingLocator = By.xpath("//tp-yt-paper-item[.//yt-formatted-string[normalize-space(text())='Gaming'] or normalize-space(.)='Gaming']");
            WebElement gaming = wait.until(ExpectedConditions.elementToBeClickable(gamingLocator));
            gaming.click();

            wait.until(ExpectedConditions.titleContains("Gaming"));
            wait.until(ExpectedConditions.urlContains("/gaming"));
            assertTrue(driver.getTitle().contains("Gaming"), "Title should contain Gaming");
            assertTrue(driver.getCurrentUrl().contains("/gaming"), "URL should contain /gaming");
        } catch (Exception e) {
            try {
                File screenshot = ((TakesScreenshot) driver).getScreenshotAs(OutputType.FILE);
                Files.copy(screenshot.toPath(), new File("failure_youtube_navigate.png").toPath());
            } catch (Exception ignore) {}
            fail("Test failed: " + e.getMessage());
        }
    }
}