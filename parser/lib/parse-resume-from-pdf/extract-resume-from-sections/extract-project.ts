import type { ResumeProject } from '../../redux/resume-types.ts';
import type { FeatureSet, ResumeSectionToLines, TextScores } from '../types.ts';
import { getBulletPointsFromLines, getDescriptionsLineIdx } from './lib/bullet-points.ts';
import { DATE_FEATURE_SETS, getHasText, isBold } from './lib/common-features.ts';
import { getTextWithHighestFeatureScore } from './lib/feature-scoring-system.ts';
import { getSectionLinesByKeywords } from './lib/get-section-lines.ts';
import { divideSectionIntoSubsections } from './lib/subsections.ts';
export const extractProject = (sections: ResumeSectionToLines) => {
	const projects: ResumeProject[] = [];
	const projectsScores: { projectScores: TextScores; dateScores: TextScores }[] = [];
	const lines = getSectionLinesByKeywords(sections, ['project']);
	const subsections = divideSectionIntoSubsections(lines);

	for (const subsectionLines of subsections) {
		const descriptionsLineIdx = getDescriptionsLineIdx(subsectionLines) ?? 1;

		const subsectionInfoTextItems = subsectionLines.slice(0, descriptionsLineIdx).flat();
		const [date, dateScores] = getTextWithHighestFeatureScore(subsectionInfoTextItems, DATE_FEATURE_SETS);
		const PROJECT_FEATURE_SET: FeatureSet[] = [
			[isBold, 2],
			[getHasText(date), -4],
		];
		const [project, projectScores] = getTextWithHighestFeatureScore(
			subsectionInfoTextItems,
			PROJECT_FEATURE_SET,
			false
		);

		const descriptionsLines = subsectionLines.slice(descriptionsLineIdx);
		const descriptions = getBulletPointsFromLines(descriptionsLines);

		projects.push({ project, date, descriptions });
		projectsScores.push({
			projectScores,
			dateScores,
		});
	}
	return { projects, projectsScores };
};
