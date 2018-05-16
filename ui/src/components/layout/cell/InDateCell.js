import React from 'react';
import classnames from 'classnames';
import { Tooltip } from 'reactstrap';
import { DAYS, PRIORITIES_LABEL } from '../../../constants/constants';

class InDateCell extends React.PureComponent {
  constructor(props) {
    super(props);

    this.state = {};
    this.toggleTooltip = this.toggleTooltip.bind(this);
  }

  toggleTooltip() {
    this.setState({ tooltipOpen: !this.state.tooltipOpen });
  }

  renderPriorities() {
    const { priorities, minDays, rowId } = this.props;
    return priorities.map((item, i) => <div key={`date-priority-${rowId}-${i}`}>{`${minDays + i} ${DAYS}: ${item}%`}</div>);
  }

  render() {
    const { value, priorities, rowId } = this.props;
    const hasPriorities = priorities !== null;

    const className = classnames({
      'in-dates-td': true,
      'with-priorities': hasPriorities
    });

    return (
      <div className={className}>
        <span id={rowId}>{value}</span>
        { hasPriorities ?
          <Tooltip placement="right" isOpen={this.state.tooltipOpen} target={rowId} toggle={this.toggleTooltip}>
            <div>{PRIORITIES_LABEL}:</div>
            {this.renderPriorities()}
          </Tooltip>
          : null }
      </div>
    );
  }
}

export default InDateCell;
