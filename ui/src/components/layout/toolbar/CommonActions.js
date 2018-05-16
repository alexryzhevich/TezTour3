import React from 'react';
import { Button } from 'reactstrap';
import {
  END_EDIT,
  SAVE_BUTTON_TITLE
} from '../../../constants/constants';

class CommonActions extends React.PureComponent {
  render() {
    const {
      canSave,
      closeEditMode,
      save
    } = this.props;

    return (
      <div>
        <Button
          color="danger"
          onClick={closeEditMode}
        >
          { END_EDIT }
        </Button>
        <Button
          color={canSave ? 'success' : 'secondary'}
          onClick={save}
          disabled={!canSave}
        >
          { SAVE_BUTTON_TITLE }
        </Button>
      </div>
    );
  }
}

export default CommonActions;
