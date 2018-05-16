import React, { Component } from 'react';
import moment from 'moment';
import { Col, Button, Row } from 'reactstrap';
import { FaPlus } from 'react-icons/lib/fa';
import { DateRangePicker } from 'react-dates';
import 'react-dates/lib/css/_datepicker.css';
import { BEGINNING_LABEL, END_LABEL } from '../../../constants/constants';

const DATE_FORMAT = 'YYYY-MM-DD';
const UI_DATE_FORMAT = 'DD.MM.YYYY';


class DateRange extends Component {
  constructor(props) {
    super(props);

    this.state = {
      startDate: null,
      endDate: null,
      focusedInput: null
    };

    this.onDatesChange = this.onDatesChange.bind(this);
    this.onFocusChange = this.onFocusChange.bind(this);
    this.isOutsideRange = this.isOutsideRange.bind(this);
    this.addInterval = this.addInterval.bind(this);
  }

  onDatesChange({ startDate, endDate }) {
    this.setState({ startDate, endDate });
  }

  onFocusChange(focusedInput) {
    this.setState({ focusedInput });
  }

  isOutsideRange(day) {
    const { allowedDates } = this.props;
    return !allowedDates.includes(moment(day).format(DATE_FORMAT));
  }

  addInterval() {
    const { startDate, endDate } = this.state;
    const newStartDate = !startDate ? null : startDate.format(UI_DATE_FORMAT);
    const newEndDate = !endDate ? null : endDate.format(UI_DATE_FORMAT);
    this.props.onSubmit({ startDate: newStartDate, endDate: newEndDate });
    this.setState({ startDate: null, endDate: null });
  }

  render() {
    const { startDate, endDate, focusedInput } = this.state;
    const isAddIntervalDisabled = !startDate || !endDate;

    return (
      <Row className="date-range-row">
        <Col sm={9} className="text-right">
          <DateRangePicker
            startDate={startDate}
            startDateId="dateRangeStartDate"
            endDate={endDate}
            endDateId="dateRangeEndDate"
            startDatePlaceholderText={BEGINNING_LABEL}
            endDatePlaceholderText={END_LABEL}
            onDatesChange={this.onDatesChange}
            focusedInput={focusedInput}
            onFocusChange={this.onFocusChange}
            isOutsideRange={this.isOutsideRange}
            displayFormat={UI_DATE_FORMAT}
            firstDayOfWeek={1}
          />
        </Col>
        <Col sm={3} className="text-left">
          <Button
            disabled={isAddIntervalDisabled}
            onClick={this.addInterval}
          >
            <FaPlus className="plus-icon" />
          </Button>
        </Col>
      </Row>
    );
  }
}

export default DateRange;
