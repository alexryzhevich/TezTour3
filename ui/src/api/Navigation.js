import history from '../history';

export const LAYOUTS_URL = '/layouts/';

export const LAYOUT_CREATION_URL = '/layouts/new';

export const LOGIN_URL = '/auth/login/';

export const LOGOUT_URL = '/auth/logout/';

export const PRECOMPUTE_URL = `${LAYOUTS_URL}precompute/`;

export const UPLOAD_CURRENT_FILE_URL = `${LAYOUTS_URL}save-current-file/`;

export const getExtendEditModeUrl = layoutId => `${LAYOUTS_URL}${layoutId}/edit/`;

export const getLayoutUpdateUrl = id => `${LAYOUTS_URL}${id}/init/`;

export const deleteLayoutUrl = id => `${LAYOUTS_URL}${id}/`;

export const getLayoutUrl = layoutId => `${LAYOUTS_URL}${layoutId}/`;

export const getLayoutUpdateFromCurrentFileUrl = layoutId => `${LAYOUTS_URL}${layoutId}/update-from-current/`;

export const goToLayoutCreation = () => {
  const url = `${LAYOUT_CREATION_URL}`;
  history.push(url);
};

export const goToInitializationStep = id => () => {
  const url = `${LAYOUTS_URL}${id}/init`;
  history.push(url);
};

export const goToLayout = (id) => {
  const url = `${LAYOUTS_URL}${id}`;
  history.push(url);
};
