import { fromServerFormat } from '../components/util/formatData';
import { calculateLosses } from '../components/util/calculateLosses';
import { goToInitializationStep } from '../api/Navigation';
import {
  EDIT_MODE_ON,
  RESET_EDIT_MODE,
  UPDATE_LAYOUT_DATA,
  TOGGLE_AUTOPRECOMPUTE,
  HANDLE_PRECOMPUTED_DATA,
  UPDATE_CELLS,
  TOGGLE_PRIORITIES_MODAL,
  TOGGLE_LOSSES_MODAL,
  TOGGLE_UPDATE_FROM_FILE_MODAL,
  SAVE_LAYOUT_PRIORITIES,
  CLOSE_EDIT_PRIORITIES_MODE,
  OPEN_EDIT_PRIORITIES_MODE,
  TOGGLE_SHOW_LOSSES,
} from '../constants/actions/layout';


export const openEditMode = payload => ({
  type: EDIT_MODE_ON,
  payload,
});

export const updateCells = newData => ({
  type: UPDATE_CELLS,
  newData,
});

export const toggleAutoPrecompute = () => ({
  type: TOGGLE_AUTOPRECOMPUTE,
});

export const handlePrecomputedData = data => (dispatch) => {
  const formattedData = fromServerFormat(data);
  const lossesData = calculateLosses(formattedData);

  dispatch({
    type: HANDLE_PRECOMPUTED_DATA,
    formattedData,
    lossesData,
  });
};

export const resetEditMode = () => (dispatch, getState) => {
  const { extendTimeout } = getState().layout.toolbar.editMode;

  if (extendTimeout) {
    clearTimeout(extendTimeout);
  }

  dispatch({
    type: RESET_EDIT_MODE,
  });
};

export const updateLayoutData = serverData => (dispatch) => {
  const { id } = serverData;

  if (serverData.dates.length === 0) {
    goToInitializationStep(id)();
  }

  const formattedData = fromServerFormat(serverData);
  const lossesData = calculateLosses(formattedData);
  const payload = { serverData, formattedData, lossesData };

  dispatch({
    type: UPDATE_LAYOUT_DATA,
    payload,
  });
};

export const togglePrioritiesModal = payload => ({
  type: TOGGLE_PRIORITIES_MODAL,
  payload,
});

export const toggleLossesModal = dateType => ({
  type: TOGGLE_LOSSES_MODAL,
  dateType,
});

export const toggleUpdateFromFileModal = payload => ({
  type: TOGGLE_UPDATE_FROM_FILE_MODAL,
  payload,
});

export const saveLayoutPriorities = newPriorities => ({
  type: SAVE_LAYOUT_PRIORITIES,
  newPriorities,
});

export const openEditPrioritiesMode = () => ({
  type: OPEN_EDIT_PRIORITIES_MODE,
});

export const closeEditPrioritiesMode = () => ({
  type: CLOSE_EDIT_PRIORITIES_MODE,
});

export const toggleShowLosses = () => ({
  type: TOGGLE_SHOW_LOSSES,
});
