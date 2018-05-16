import React from 'react';
import range from 'lodash/range';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import update from 'immutability-helper';
import Cell from './cell/Cell';
import StaticCell from './cell/StaticCell';
import InDateCell from './cell/InDateCell';
import LayoutTable from './table';
import { apiPost } from '../../actions/api';
import { toServerFormat } from '../util/formatData';
import errors from '../util/error/errorMessages';
import {
  updateCells,
  handlePrecomputedData
} from '../../actions/layout';
import { setError } from '../../actions/ui';
import {
  OUT_PLACES_COL,
  IN_PLACES_COL,
  IN_DATES_COL,
  OUT_DATES_COL,
  LAYOUT_COL,
  PLACE_DEFAULT_VALUE
} from '../../constants/constants';
import { PRECOMPUTE_URL } from '../../api/Navigation';

const formatDate = value => (value ? new Date(value).toLocaleDateString('ru-RU') : value);


class Layout extends React.Component {
  constructor(props) {
    super(props);

    this.state = {};

    this.updateColumns = this.updateColumns.bind(this);
    this.updateCell = this.updateCell.bind(this);
    this.generateColumns = this.generateColumns.bind(this);
    this.validateChange = this.validateChange.bind(this);
  }

  componentDidMount() {
    this.updateColumns(this.props);
  }

  componentWillReceiveProps(nextProps) {
    if (this.props.editMode.isEnabled === nextProps.editMode.isEnabled
      && this.props.data.serverData === nextProps.data.serverData) {
      return;
    }
    this.updateColumns(nextProps);
  }

  updateColumns(nextProps) {
    if (!nextProps.data.serverData) {
      return;
    }

    this.setState({
      columns: this.generateColumns(nextProps)
    });
  }

  updateCell(cellInfo) {
    const { serverData, formattedData } = this.props.data;
    const { isEnabled, autoPrecompute } = this.props.editMode;
    const { rowIndex, columnIndex } = cellInfo;

    const data = update(formattedData, {
      [rowIndex]: { places: { [columnIndex]: { $set: cellInfo } } }
    });

    if (autoPrecompute && isEnabled) {
      const reformattedData = toServerFormat(data, serverData);
      this.props.apiPost(
        PRECOMPUTE_URL,
        reformattedData,
        this.props.handlePrecomputedData,
        null,
        null,
        true
      );
    }

    this.props.updateCells(data);
  }

  validateChange(r, c, value) {
    const { serverData, formattedData: data } = this.props.data;
    const { width } = serverData;

    let horizontalSum = value;
    for (let i = 0; i < data[r].places.length; i += 1) {
      if ((!data[r].places[i].required && !data[r].places[i].outOfOrder)
        || r % width === i
        || data[r].places[i].value === PLACE_DEFAULT_VALUE
        || i === c) {
        continue;
      }
      horizontalSum += data[r].places[i].value;
    }
    if (horizontalSum > data[r].outAmount) {
      this.props.setError(errors.buildUIError(`Недостаточно мест обратно. Указазанное количество мест на ${horizontalSum - data[r].outAmount} превышает доступное.`));
      return false;
    }

    const inDate = c + (Math.trunc((r - c) / width) * width);
    const { inAmount } = data[inDate];
    let verticalSum = value;
    for (let i = 1; i < width + 1 && i + inDate < data.length; i += 1) {
      const val = data[inDate + i].places[c].value;
      if (val === PLACE_DEFAULT_VALUE
        || (!data[inDate + i].places[c].required && !data[inDate + i].places[c].outOfOrder)
        || inDate + i === r) {
        continue;
      }
      verticalSum += val;
    }
    if (verticalSum > inAmount) {
      this.props.setError(errors.buildUIError(`Недостаточно мест туда. Указазанное количество мест на ${verticalSum - inAmount} превышает доступное.`));
      return false;
    }
    return true;
  }

  generateColumns(nextProps) {
    const { width, minDays } = nextProps.data.serverData;

    return [
      {
        Header: IN_DATES_COL,
        columns: [{
          accessor: r => r.inDate,
          id: 'arrivalDate',
          Cell: (row) => {
            const props = {
              value: formatDate(row.value),
              priorities: row.original.priorities,
              rowId: `layout-row-${row.original._id}`, // eslint-disable-line no-underscore-dangle
              minDays,
            };

            return <InDateCell {...props} />;
          }
        }]
      },
      {
        Header: IN_PLACES_COL,
        columns: [{
          accessor: r => r.inAmount,
          id: 'arrivalAmount',
          Cell: row =>
            (
              <div className="in-places-td">
                {row.value}
                <span>{row.original.inDate ? '/' : ''}</span>
                <span className="losses-td">{row.original.inLosses}</span>
              </div>
            )
        }]
      },
      {
        Header: LAYOUT_COL,
        columns: range(0, width)
          .map((item, i) => ({
            accessor: r => r.places[i],
            id: `place${i}`,
            minWidth: 50,
            Cell: (row) => {
              const { editable } = row.value;

              if (!editable) {
                return <StaticCell {...row.value} />;
              }

              const props = {
                data: row.value,
                update: this.updateCell,
                validate: this.validateChange
              };

              return <Cell {...props} />;
            }
          }))
      },
      {
        Header: OUT_PLACES_COL,
        columns: [{
          accessor: r => r.outAmount,
          id: 'departureAmount',
          Cell: row =>
            (
              <div className="out-places-td">
                {row.value}
                <span>{row.original.outDate ? '/' : ''}</span>
                <span className="losses-td">{row.original.outLosses}</span>
              </div>
            )
        }]
      },
      {
        Header: OUT_DATES_COL,
        columns: [{
          accessor: r => r.outDate,
          id: 'departureDate',
          Cell: (row) => {
            const value = formatDate(row.value);

            return <div className="out-dates-td">{value}</div>;
          }
        }]
      }
    ];
  }

  render() {
    const { columns } = this.state;
    const { formattedData: data } = this.props.data;
    const { isEditPrioritiesModeEnabled } = this.props;

    if (!columns || !data) {
      return null;
    }

    const props = {
      isSelectable: isEditPrioritiesModeEnabled,
      columns,
      data
    };

    return <LayoutTable {...props} />;
  }
}

const mapStateToProps = state => ({
  editMode: state.layout.toolbar.editMode,
  isEditPrioritiesModeEnabled: state.layout.toolbar.editPrioritiesMode.isEnabled,
  data: state.layout.data
});

const mapDispatchToProps = dispatch => bindActionCreators({
  setError,
  updateCells,
  handlePrecomputedData,
  apiPost,
}, dispatch);

export default connect(mapStateToProps, mapDispatchToProps)(Layout);
