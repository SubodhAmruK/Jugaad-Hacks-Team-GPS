import express, { response } from "express";
import { dirname } from "path";
import { fileURLToPath } from "url";
import bodyParser from "body-parser";
import languages from './languages.js';
import translate from 'translate-google';
const __dirname = dirname(fileURLToPath(import.meta.url));
const app = express();
const port = 3000;

// Set EJS as the view engine
app.set('view engine', 'ejs');
app.set('views', __dirname+"/views"); // Set the views directory
app.use(express.static(__dirname+"/public"));

app.use(bodyParser.urlencoded({ extended: true }));

const languageCodeMap = {};
languages.forEach(lang => {
    languageCodeMap[lang.name] = lang.code;
});
app.post("/drawpage", (req, res) => {
    res.sendFile(__dirname+"/views/index.html");
});
app.post("/todo", (req, res) => {
    res.sendFile(__dirname+"/views/todo.html");
});

app.post("/usetext", (req, res) => {
    const textcontent = req.body.tcontent;
    const languageCode = req.body.Languagecode;

    if (!languageCode) {
        res.status(400).send("Invalid language name");
        return;
    }

    translate(textcontent, { to: languageCode })
        .then(translationResult => {
            res.render('usetext', { languages: languages, result: translationResult }); 
        })
        .catch(err => {
            console.error(err);
            res.status(500).send("Error translating text");
        });
});

app.get("/", (req, res) => {
    res.render('usetext', { languages: languages, result: '' }); // Pass languages to the template
});

app.listen(port, () => {
    console.log(`listening on port ${port}`);
});
