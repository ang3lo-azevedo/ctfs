import com.aspose.words.Document;
import com.aspose.words.SaveFormat;
import com.aspose.words.NativeLibSettings;

public class DocxToPngConverter {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("Usage: DocxToPngConverter <input.docx> <output.png>");
            System.exit(1);
        }
        NativeLibSettings.setUseJAIImageRendering(true);
        Document doc = new Document(args[0]);
        doc.save(args[1], SaveFormat.PNG);
    }
}
