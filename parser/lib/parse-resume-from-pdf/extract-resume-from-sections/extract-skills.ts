import { deepClone } from '../../deep-clone.ts';
import type { ResumeSkills } from '../../redux/resume-types.ts';
import { initialFeaturedSkills } from '../../redux/resumeSlice.ts';
import type { ResumeSectionToLines } from '../types.ts';
import { getBulletPointsFromLines, getDescriptionsLineIdx } from './lib/bullet-points.ts';
import { getSectionLinesByKeywords } from './lib/get-section-lines.ts';

export const extractSkills = (sections: ResumeSectionToLines) => {
	const lines = getSectionLinesByKeywords(sections, ['skill']);
	const descriptionsLineIdx = getDescriptionsLineIdx(lines) ?? 0;
	const descriptionsLines = lines.slice(descriptionsLineIdx);
	const descriptions = getBulletPointsFromLines(descriptionsLines);

	const featuredSkills = deepClone(initialFeaturedSkills);
	if (descriptionsLineIdx !== 0) {
		const featuredSkillsLines = lines.slice(0, descriptionsLineIdx);
		const featuredSkillsTextItems = featuredSkillsLines
			.flat()
			.filter((item) => item.text.trim())
			.slice(0, 6);
		for (let i = 0; i < featuredSkillsTextItems.length; i++) {
			featuredSkills[i].skill = featuredSkillsTextItems[i].text;
		}
	}

	const skills: ResumeSkills = {
		featuredSkills,
		descriptions,
	};

	return { skills };
};
