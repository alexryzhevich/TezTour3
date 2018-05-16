import fill from 'lodash/fill';
import { PLACE_DEFAULT_VALUE } from '../../constants/constants';

const MILLISECONDS_PER_DAY = 1000 * 60 * 60 * 24;

const getPlaceValues = (inDate, outDate, dates, width) => {
  const columnIndex = inDate % width;
  const rowIndex = outDate;

  const diagonalInDate = columnIndex + (Math.trunc((rowIndex - columnIndex) / width) * width);
  const { inAmount } = dates[diagonalInDate];

  return {
    columnIndex,
    rowIndex,
    inAmount
  };
};

const dateDiffInDays = (a, b) => {
  const utc1 = Date.UTC(a.getFullYear(), a.getMonth(), a.getDate());
  const utc2 = Date.UTC(b.getFullYear(), b.getMonth(), b.getDate());

  return Math.floor((utc2 - utc1) / MILLISECONDS_PER_DAY);
};

const appendPossibleOutOfOrderPlaces = (data, width, durationLimit) => {
  for (let i = 0; i < data.length - 1; i += 1) {
    const columnIndex = i % width;

    if (!data[i].inDate) {
      continue;
    }

    for (let j = i + 1; j < data.length; j += 1) {
      const date1 = new Date(data[i].inDate);
      const date2 = new Date(data[j].outDate);

      if (!data[j].outDate) {
        continue;
      }

      const passedDays = dateDiffInDays(date1, date2);
      if (passedDays > durationLimit) {
        break;
      }

      const rowIndex = j;

      data[rowIndex].places[columnIndex] = {
        ...data[rowIndex].places[columnIndex],
        columnIndex,
        rowIndex,
        editable: true,
        passedDays
      };
    }
  }

  return data;
};

export function fromServerFormat(data) {
  const {
    dates, width, durationLimit, places, outOfOrder
  } = data;

  const result = dates.map((item, i) => {
    const columnIndex = i % width;
    const places = fill(Array(width), {
      value: PLACE_DEFAULT_VALUE,
      editable: false
    });

    places[columnIndex] = {
      ...places[columnIndex],
      diagonal: true,
      value: item.inAmount
    };

    return {
      _id: i,
      ...item,
      places
    };
  });

  places.forEach(({
    inDate, outDate, amount, required
  }) => {
    const { columnIndex, rowIndex, inAmount } = getPlaceValues(inDate, outDate, dates, width);

    result[outDate].places[columnIndex] = {
      ...result[outDate].places[columnIndex],
      rowIndex,
      columnIndex,
      inAmount,
      editable: true,
      required: required || false,
      value: amount
    };
  });

  outOfOrder.forEach(({
    inDate, outDate, amount, autoChanged
  }) => {
    const { columnIndex, rowIndex, inAmount } = getPlaceValues(inDate, outDate, dates, width);

    result[outDate].places[columnIndex] = {
      ...result[outDate].places[columnIndex],
      rowIndex,
      columnIndex,
      inAmount,
      autoChanged,
      editable: true,
      outOfOrder: true,
      value: amount
    };
  });

  return appendPossibleOutOfOrderPlaces(result, width, durationLimit);
}

export function toServerFormat(data, previousData, priorities, selectedDates = [], datesPriorities = [], noLosses = null) {
  const { width } = previousData;
  const newDates = [];
  const newPlaces = [];
  const newOutOfOrder = [];
  for (let i = 0; i < data.length; i += 1) {
    const {
      _id, inAmount, inLosses, outAmount, outLosses, inDate, outDate, places, priorities, inNoLosses, outNoLosses
    } = data[i];

    const newDate = {
      inAmount,
      inLosses,
      outAmount,
      outLosses,
      inDate,
      outDate,
      inNoLosses: noLosses ? noLosses[i][0] : inNoLosses,
      outNoLosses: noLosses ? noLosses[i][1] : outNoLosses,
      priorities: selectedDates.includes(_id) ? datesPriorities : priorities
    };

    newDates.push(newDate);

    for (let j = 0; j < places.length; j += 1) {
      if (places[j].value === PLACE_DEFAULT_VALUE || i % width === j) {
        continue;
      }

      const {
        value: amount,
        required,
        outOfOrder,
        autoChanged
      } = places[j];
      const outDate = i;
      const inDate = j + (Math.trunc((i - j) / width) * width);

      const place = {
        outDate,
        inDate,
        amount
      };

      if (outOfOrder) {
        newOutOfOrder.push({ ...place, autoChanged });
      } else {
        newPlaces.push({ ...place, required });
      }
    }
  }
  const prioritiesObject = priorities ? { priorities } : {};
  return {
    ...previousData,
    ...prioritiesObject,
    dates: newDates,
    places: newPlaces,
    outOfOrder: newOutOfOrder
  };
}

