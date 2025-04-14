import fs from 'fs';
import { parse } from 'json2csv';
import path from 'path';
import { fileURLToPath } from 'url';
import { parseResumeFromPdf } from './parse-resume-from-pdf/index.ts';

// Fix for __dirname in ES module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Get file path from command-line arguments
const filePath = process.argv[2];

parseResumeFromPdf(filePath)
	.then((resume) => {
		console.log(JSON.stringify(resume, null, 2));

		// ✨ Save path setup
		const outputDir = path.join(__dirname, '../parsed_resumes');
		const baseName = path.basename(filePath, path.extname(filePath));
		const jsonPath = path.join(outputDir, `${baseName}.json`);
		// const csvPath = path.join(outputDir, `${baseName}.csv`);

		// Make sure output dir exists
		fs.mkdirSync(outputDir, { recursive: true });

		// Save JSON
		fs.writeFileSync(jsonPath, JSON.stringify(resume, null, 2), 'utf-8');

		// Save CSV (assumes resume is flat — you may need to flatten deeply nested fields)
		// const csv = parse(resume);
		// fs.writeFileSync(csvPath, csv, 'utf-8');

		console.log(`Saved parsed data to:\n- ${jsonPath}`); //\n- ${csvPath}
	})
	.catch((err) => {
		console.error('Error parsing resume:', err);
		process.exit(1);
	});
