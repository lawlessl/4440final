import path from 'path';
import { fileURLToPath } from 'url';
import type { ResumeWorkExperience } from '../../redux/resume-types.ts';
import type { FeatureSet, ResumeSectionToLines, TextItem, TextScores } from '../types.ts';
import { getBulletPointsFromLines, getDescriptionsLineIdx } from './lib/bullet-points.ts';
import { DATE_FEATURE_SETS, getHasText, hasNumber, isBold } from './lib/common-features.ts';
import { getTextWithHighestFeatureScore } from './lib/feature-scoring-system.ts';
import { getSectionLinesByKeywords } from './lib/get-section-lines.ts';
import { divideSectionIntoSubsections } from './lib/subsections.ts';

// prettier-ignore
const WORK_EXPERIENCE_KEYWORDS_LOWERCASE = ['work', 'experience', 'employment', 'history', 'job'];
// prettier-ignore
const JOB_TITLES = ['Accountant', 'Administrator', 'Advisor', 'Agent', 'Analyst', 'Apprentice', 'Architect', 'Assistant', 'Associate', 'Auditor', 'Bartender', 'Biologist', 'Bookkeeper', 'Buyer', 'Carpenter', 'Cashier', 'CEO', 'Clerk', 'Co-op', 'Co-Founder', 'Consultant', 'Coordinator', 'CTO', 'Developer', 'Development', 'Designer', 'Director', 'Driver', 'Editor', 'Electrician', 'Engineer', 'Extern', 'Founder', 'Freelancer', 'Head', 'Intern', 'Janitor', 'Journalist', 'Laborer', 'Lawyer', 'Lead', 'Manager', 'Mechanic', 'Member', 'Nurse', 'Officer', 'Operator', 'Operation', 'Photographer', 'President', 'Producer', 'Recruiter', 'Representative', 'Researcher', 'Sales', 'Server', 'Scientist', 'Specialist', 'Supervisor', 'Teacher', 'Technician', 'Trader', 'Trainee', 'Treasurer', 'Tutor', 'Vice', 'VP', 'Volunteer', 'Webmaster', 'Worker'];

// Simulate __dirname for ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const hasJobTitle = (item: TextItem) =>
	JOB_TITLES.some((jobTitle) => item.text.split(/\s/).some((word) => word === jobTitle));
const hasMoreThan5Words = (item: TextItem) => item.text.split(/\s/).length > 5;
const JOB_TITLE_FEATURE_SET: FeatureSet[] = [
	[hasJobTitle, 4],
	[hasNumber, -4],
	[hasMoreThan5Words, -2],
];

export const extractWorkExperience = (sections: ResumeSectionToLines) => {
	const workExperiences: ResumeWorkExperience[] = [];
	const workExperiencesScores: { companyScores: TextScores; jobTitleScores: TextScores; dateScores: TextScores }[] = [];
	const lines = getSectionLinesByKeywords(sections, WORK_EXPERIENCE_KEYWORDS_LOWERCASE);
	const subsections = divideSectionIntoSubsections(lines);

	for (const subsectionLines of subsections) {
		const descriptionsLineIdx = getDescriptionsLineIdx(subsectionLines) ?? 2;

		const subsectionInfoTextItems = subsectionLines.slice(0, descriptionsLineIdx).flat();
		const [date, dateScores] = getTextWithHighestFeatureScore(subsectionInfoTextItems, DATE_FEATURE_SETS);
		const [jobTitle, jobTitleScores] = getTextWithHighestFeatureScore(subsectionInfoTextItems, JOB_TITLE_FEATURE_SET);
		const COMPANY_FEATURE_SET: FeatureSet[] = [
			[isBold, 2],
			[getHasText(date), -4],
			[getHasText(jobTitle), -4],
		];
		const [company, companyScores] = getTextWithHighestFeatureScore(
			subsectionInfoTextItems,
			COMPANY_FEATURE_SET,
			false
		);

		const subsectionDescriptionsLines = subsectionLines.slice(descriptionsLineIdx);
		const descriptions = getBulletPointsFromLines(subsectionDescriptionsLines);

		workExperiences.push({ company, jobTitle, date, descriptions });
		workExperiencesScores.push({
			companyScores,
			jobTitleScores,
			dateScores,
		});
	}
	return { workExperiences, workExperiencesScores };
};
