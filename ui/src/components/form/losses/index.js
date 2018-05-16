import React from 'react';
import { Button, Row, Col } from 'reactstrap';
import { GoX } from 'react-icons/lib/go';
import DateRange from './DateRange';
import {
  CANCEL_BUTTON_TITLE,
  SAVE_BUTTON_TITLE,
  LOSSES_RESTRICTION_PERIOD
} from '../../../constants/constants';
import './LossesForm.css';

const Buttons = ({ hasErrors, onCancel, onSubmit }) => (
  <Col sm={12} className="text-right">
    <Button className="left-btn" color="default" onClick={onCancel}>{CANCEL_BUTTON_TITLE}</Button>
    <Button color="primary" onClick={onSubmit} disabled={hasErrors}>{SAVE_BUTTON_TITLE}</Button>
  </Col>
);

class LossesForm extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      intervals: []
    };

    this.onSubmit = this.onSubmit.bind(this);
    this.addInterval = this.addInterval.bind(this);
    this.removeInterval = this.removeInterval.bind(this);
  }

  componentWillMount() {
    this.setState({ intervals: [...this.props.intervals] });
  }

  onSubmit() {
    this.props.onSubmit(this.state.intervals);
  }

  addInterval({ startDate, endDate }) {
    const { intervals } = this.state;
    if (!startDate || !endDate) {
      return;
    }
    const newIntervals = [...intervals];
    newIntervals.push({ startDate, endDate });
    this.setState({ intervals: newIntervals });
  }

  removeInterval(idx) {
    return () => {
      const { intervals } = this.state;
      if (idx >= intervals.length || idx < 0) {
        return;
      }
      const newIntervals = [...intervals];
      newIntervals.splice(idx, 1);
      this.setState({ intervals: newIntervals });
    };
  }

  renderIntervals(intervals) {
    return intervals.map((int, num) => (
      <Row key={`no-losses-int-${num}`} className="no-losses-interval-row justify-content-sm-center">
        <Col sm="auto" className="no-losses-interval">
          {int.startDate} - {int.endDate}
        </Col>
        <Col sm={2} className="text-left">
          <Button
            color="secondary"
            outline
            size="sm"
            onClick={this.removeInterval(num)}
          >
            <GoX />
          </Button>
        </Col>
      </Row>));
  }

  render() {
    const {
      invalid, toggle, dates
    } = this.props;
    const { intervals } = this.state;

    return (
      <Row>
        <Col sm={12} className="text-center">
          <h4>{LOSSES_RESTRICTION_PERIOD}</h4>
        </Col>
        <Col sm={12}>
          { this.renderIntervals(intervals) }
        </Col>
        <Col sm={12}>
          <DateRange
            allowedDates={dates}
            onSubmit={this.addInterval}
          />
        </Col>
        <Buttons
          hasErrors={invalid}
          onCancel={toggle}
          onSubmit={this.onSubmit}
        />
      </Row>
    );
  }
}

export default LossesForm;
