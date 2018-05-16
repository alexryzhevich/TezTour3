import React from 'react';
import {
  Button,
  ButtonDropdown,
  DropdownToggle,
  DropdownMenu,
  DropdownItem
} from 'reactstrap';
import Toggle from 'react-toggle';
import 'react-toggle/style.css';
import {
  AUTO_RECALCULATION,
  EDIT_PRIORITIES,
  EDIT_DATES_PRIORITIES,
  LOSSES_RESTRICTION_PERIOD,
  IN_LABEL,
  OUT_LABEL,
  MAKE_RECALCULATION,
  RESET_BUTTON_TITLE,
  UPDATE_FROM_FILE_BUTTON_TITLE,
  OPTIONS_DROPDOWN,
  FROM_CURRENT_FILE_BUTTON_TITLE,
  CHOOSE_FILE_BUTTON_TITLE
} from '../../../../constants/constants';

class EditModePanel extends React.PureComponent {
  constructor(props) {
    super(props);

    this.state = {
      isOptionsDropdownOpen: false,
      isUpdateDropdownOpen: false,
    };

    this.toggleOptionsDropdown = this.toggleOptionsDropdown.bind(this);
    this.toggleUpdateDropdown = this.toggleUpdateDropdown.bind(this);
    this.openInLossesModal = this.openInLossesModal.bind(this);
    this.openOutLossesModal = this.openOutLossesModal.bind(this);
  }

  toggleOptionsDropdown() {
    this.setState(prevState => ({
      isOptionsDropdownOpen: !prevState.isOptionsDropdownOpen
    }));
  }

  toggleUpdateDropdown() {
    this.setState(prevState => ({
      isUpdateDropdownOpen: !prevState.isUpdateDropdownOpen
    }));
  }

  openInLossesModal() {
    this.props.openLossesModal('in');
  }

  openOutLossesModal() {
    this.props.openLossesModal('out');
  }

  render() {
    const { isOptionsDropdownOpen, isUpdateDropdownOpen } = this.state;
    const {
      hasChanges,
      autoPrecompute,
      canSave,
      toggleUpdateFromFileModal,
      openPrioritiesModal,
      openEditPrioritiesMode,
      reset,
      toggleAutoPrecompute,
      precompute,
      updateFromCurrentFile,
    } = this.props;

    return (
      <div>
        <ButtonDropdown
          isOpen={isUpdateDropdownOpen}
          toggle={this.toggleUpdateDropdown}
          disabled={hasChanges || canSave}
        >
          <DropdownToggle
            caret
            disabled={hasChanges || canSave}
            color={!hasChanges && !canSave ? 'primary' : 'secondary'}
          >
            {UPDATE_FROM_FILE_BUTTON_TITLE}
          </DropdownToggle>
          <DropdownMenu>
            <DropdownItem onClick={toggleUpdateFromFileModal}>
              {CHOOSE_FILE_BUTTON_TITLE}
            </DropdownItem>
            <DropdownItem onClick={updateFromCurrentFile}>
              {FROM_CURRENT_FILE_BUTTON_TITLE}
            </DropdownItem>
          </DropdownMenu>
        </ButtonDropdown>
        <ButtonDropdown
          isOpen={isOptionsDropdownOpen}
          toggle={this.toggleOptionsDropdown}
        >
          <DropdownToggle caret>
            { OPTIONS_DROPDOWN }
          </DropdownToggle>
          <DropdownMenu>
            <DropdownItem onClick={openPrioritiesModal}>
              { EDIT_PRIORITIES }
            </DropdownItem>
            <DropdownItem onClick={openEditPrioritiesMode}>
              { EDIT_DATES_PRIORITIES }
            </DropdownItem>
            <DropdownItem divider />
            <DropdownItem header>
              { LOSSES_RESTRICTION_PERIOD }
            </DropdownItem>
            <DropdownItem onClick={this.openInLossesModal}>
              { IN_LABEL }
            </DropdownItem>
            <DropdownItem onClick={this.openOutLossesModal}>
              { OUT_LABEL }
            </DropdownItem>
            <DropdownItem divider />
            <DropdownItem
              className="danger"
              onClick={reset}
            >
              { RESET_BUTTON_TITLE }
            </DropdownItem>
            <DropdownItem>
              <label
                htmlFor="autoprecompute"
                className="toggle-label"
              >
                <span className="toggle-label-text">
                  { AUTO_RECALCULATION }
                </span>
                <Toggle
                  defaultChecked={autoPrecompute}
                  onChange={toggleAutoPrecompute}
                  name="autoprecompute"
                />
              </label>
            </DropdownItem>
          </DropdownMenu>
        </ButtonDropdown>
        <Button
          color={hasChanges && !autoPrecompute ? 'warning' : 'secondary'}
          onClick={precompute}
          disabled={!hasChanges || autoPrecompute}
        >
          { MAKE_RECALCULATION }
        </Button>
      </div>
    );
  }
}

export default EditModePanel;
