import { TOGGLE_SELECTION } from '../constants/actions/data';

export const toggleSelection = key => ({
  type: TOGGLE_SELECTION,
  key
});
