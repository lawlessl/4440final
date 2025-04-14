// Getting pdfjs to work is tricky. The following 3 lines would make it work
// https://stackoverflow.com/a/63486898/7699841
import * as pdfjs from 'pdfjs-dist/legacy/build/pdf.mjs';
// Disable the worker for Node
//pdfjs.GlobalWorkerOptions.workerSrc = '';

import path from 'path';
import { getDocument, GlobalWorkerOptions } from 'pdfjs-dist';
import type { TextItem as PdfjsTextItem } from 'pdfjs-dist/types/src/display/api.js';
import { fileURLToPath } from 'url';
import type { TextItem, TextItems } from './types';

// These two lines simulate __dirname in ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Step 1: Read pdf and output textItems by concatenating results from each page.
 *
 * To make processing easier, it returns a new TextItem type, which removes unused
 * attributes (dir, transform), adds x and y positions, and replaces loaded font
 * name with original font name.
 *
 * @example
 * const onFileChange = async (e) => {
 *     const fileUrl = URL.createObjectURL(e.target.files[0]);
 *     const textItems = await readPdf(fileUrl);
 * }
 */
export const readPdf = async (fileUrl: string): Promise<TextItems> => {
	// Correct standard font path (adjust if needed based on project structure)
	const fontDataPath = path.resolve(__dirname, '../../node_modules/pdfjs-dist/legacy/standard_fonts');

	// Ensure it ends in a trailing slash (even if `resolve` doesn't guarantee it)
	const fontDataUrl = fontDataPath.endsWith('/') ? fontDataPath : fontDataPath + '/';

	// Tell PDF.js where to find fonts globally
	const pdfFile = await getDocument({
		url: fileUrl,
		disableFontFace: true,
	}).promise;

	let textItems: TextItems = [];

	for (let i = 1; i <= pdfFile.numPages; i++) {
		// Parse each page into text content
		const page = await pdfFile.getPage(i);
		const textContent = await page.getTextContent();

		// Wait for font data to be loaded
		await page.getOperatorList();
		const commonObjs = page.commonObjs;

		// Convert Pdfjs TextItem type to new TextItem type
		const pageTextItems = textContent.items.map((item) => {
			const {
				str: text,
				dir, // Remove text direction
				transform,
				fontName: pdfFontName,
				...otherProps
			} = item as PdfjsTextItem;

			// Extract x, y position of text item from transform.
			// As a side note, origin (0, 0) is bottom left.
			// Reference: https://github.com/mozilla/pdf.js/issues/5643#issuecomment-496648719
			const x = transform[4];
			const y = transform[5];

			// Use commonObjs to convert font name to original name (e.g. "GVDLYI+Arial-BoldMT")
			// since non system font name by default is a loaded name, e.g. "g_d8_f1"
			// Reference: https://github.com/mozilla/pdf.js/pull/15659
			const fontObj = commonObjs.get(pdfFontName);
			const fontName = fontObj.name;

			// pdfjs reads a "-" as "-­‐" in the resume example. This is to revert it.
			// Note "-­‐" is "-&#x00AD;‐" with a soft hyphen in between. It is not the same as "--"
			const newText = text.replace(/-­‐/g, '-');

			const newItem = {
				...otherProps,
				fontName,
				text: newText,
				x,
				y,
			};
			return newItem;
		});

		// Some pdf's text items are not in order. This is most likely a result of creating it
		// from design softwares, e.g. canvas. The commented out method can sort pageTextItems
		// by y position to put them back in order. But it is not used since it might be more
		// helpful to let users know that the pdf is not in order.
		// pageTextItems.sort((a, b) => Math.round(b.y) - Math.round(a.y));

		// Add text items of each page to total
		textItems.push(...pageTextItems);
	}

	// Filter out empty space textItem noise
	const isEmptySpace = (textItem: TextItem) => !textItem.hasEOL && textItem.text.trim() === '';
	textItems = textItems.filter((textItem) => !isEmptySpace(textItem));

	return textItems;
};
