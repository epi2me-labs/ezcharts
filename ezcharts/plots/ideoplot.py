"""Ideoplots."""

import argparse
from typing import Optional

import pandas as pd
from pkg_resources import resource_filename

from ezcharts.plots import Plot, util

util.set_basic_logging()
logger = util.get_named_logger("ezCharts Ideograms")


class MakeRectangles(util.JSCode):
    """
    Make JSCode rectangles.

    Where:
        x left and right are given in data
        y is a categoric variable
        height is a proportion of plot-category height
    """

    def __init__(self, height: float = 0.7):
        """Instantiate the class with some jscode and some params.

        :param height: height of rectangles as proportion
            of y-axis category height.
        """
        self.height = height

        jscode = """function renderItem(params, api) {
            var categoryIndex = api.value(0);
            var start = api.coord([api.value(1), categoryIndex]);
            var end = api.coord([api.value(2), categoryIndex]);
            var height = api.size([0, 1])[1] * @height;
            var rectShape = echarts.graphic.clipRectByRect(
                {
                    x: start[0],
                    y: start[1] - height / 2,
                    width: end[0] - start[0],
                    height: height
                },
                {
                    x: params.coordSys.x,
                    y: params.coordSys.y,
                    width: params.coordSys.width,
                    height: params.coordSys.height
                }
            );
            return (
                rectShape && {
                    type: 'rect',
                    transition: ['shape'],
                    shape: rectShape,
                    style: api.style()

                }
            );}""".replace('@height', str(self.height))

        super().__init__(jscode)


def load_user_data(data):
    """
    Validate the user provided data.

    User data should be in ucsc track format with an additional color column:
    1	1000000	1500000	1:1000001-1500000	-0.045	+	0  COLOR

    https://genome.ucsc.edu/goldenPath/help/customTrack.html
    """
    try:
        data = data.set_axis([
            'chr',
            'start',
            'end',
            'name',
            'value',
            'strand',
            'type',
            'color'
        ], axis=1)
    except ValueError as e:
        raise Exception(f"""{e}
            ERROR:
            Track data must be in ucsc format with the following columns
            - chr
            - start
            - end
            - name
            - value
            - strand
            - type
            - color""")

    data['chr'] = data['chr'].str.replace('chr', '')
    return data


def load_bands_data(bands_df, band_types):
    """
    Load chr bands data.

    This should be in the ucsc cytoband format:
    chr1        0   2300000  p36.33    gneg
    """
    try:
        bands_df = bands_df.set_axis([
            'chr',
            'start',
            'end',
            'band',
            'type'
        ], axis=1)
    except ValueError as e:
        raise Exception(f"""{e}
            ERROR:
            Bands data must be in ucsc format with the following columns
            - chr
            - start
            - end
            - band
            - type""")

    types = dict(
        acen=util.Colors.cinnabar,
        gneg=util.Colors.white,
        gpos25=util.Colors.grey90,
        gpos50=util.Colors.grey70,
        gpos75=util.Colors.grey40,
        gpos100=util.Colors.grey20,
        gvar=util.Colors.cerulean,
        stalk=util.Colors.sandstorm)

    bands_df['color'] = bands_df['type'].map(types)
    bands_df['chr'] = bands_df['chr'].str.replace('chr', '')
    bands_df = bands_df[bands_df['type'].isin(band_types)]
    return bands_df


def load_chr_sizes(genome):
    """Load chr size data."""
    sizes = f"plots/data/ideoplots/reference/{genome}/{genome}.chrom.sizes.gz"
    sizes = pd.read_csv(
        resource_filename(
            'ezcharts',
            sizes),
        sep="\t",
        header=None)
    try:
        sizes = sizes.set_axis([
            'chr',
            'size'], axis=1)
    except ValueError as e:
        raise Exception(f"""{e}
            ERROR:
            Sizes data must be in ucsc format with the following columns
            - chr
            - size""")

    sizes['chr'] = sizes['chr'].str.replace('chr', '')
    return sizes


def ideoplot(
        band_types: list = [
            'acen',
            'gneg',
            'gpos25',
            'gpos50',
            'gpos75',
            'gpos100',
            'gvar',
            'stalk'],
        genome: str = 'hg38',
        blocks: Optional[pd.DataFrame] = None,
        tracks: Optional[pd.DataFrame] = None) -> Plot:
    """Draw an ideogram in various styles."""
    blocks_list = [
        load_bands_data(x, band_types)
        if x.name == 'bands' else load_user_data(x) for x in blocks]

    if tracks is not None:
        # load user data
        track_data = load_user_data(tracks)

    plt = Plot()

    # setup some variables that define our grid
    if tracks is None:
        top_increment = 4
        height = 4
    else:
        top_increment = 2.0
        height = 1.7

    chr_sizes = []

    sizes = load_chr_sizes(genome)

    grid = list()
    xaxis = list()
    yaxis = list()
    visual_map = list()
    top = 1

    # this keeps count of total datasets added
    master_dataset_index = 0
    logger.info('Building Ideoplot')
    logger.debug(f'Dataset index : {master_dataset_index}')
    for count, (index, row) in enumerate(sizes.iterrows()):
        chromosome = row['chr']
        logger.debug(f'- Plotting chromosome: {chromosome}')
        if "_" in row['chr']:
            continue

        chr_sizes.append({
            'value': [row['chr'], 0, row['size'], row['size']],
            'itemStyle': {
                'borderJoin': 'round',
                'color': 'rgba(0, 0, 0, 0)',
                'borderColor': util.Colors.not_black,
                'borderWidth': 5}})

        grid.append({
            'left': '3.5%',
            'top': f'{top}%',
            'width': '90%',
            'height': f'{height}%'})

        top += top_increment

        if tracks is not None:
            grid.append({
                'left': '3.5%',
                'top': f'{top}%',
                'width': '90%',
                'height': f'{height}%'})

            top += top_increment + 0.05

            # These are the grid and x/yaxis index for tracks - i.e odd
            track_grid_index = count*2 if count != 0 else 0
            logger.debug(f'Track grid index : {track_grid_index}')

            # This is the gird index and x/yaxis for chromosomes - i.e. even
            chromosome_grid_index = (count*2)+1 if count != 0 else 1
            logger.debug(f'Chromosome grid index : {chromosome_grid_index}')

            # track axes
            xaxis.append({
                'gridIndex': track_grid_index,
                'show': False,
                'max': max(sizes['size'])})

            logger.debug(f'x-axis index : {len(xaxis)}')

            yaxis.append({
                'gridIndex': track_grid_index,
                'min': -2.2,
                'max': 2.2,
                'type': 'value',
                'position': 'right',
                'interval': 2.2,
                'axisLine': {'onZero': False}})

            logger.debug(f'y-axis index : {len(yaxis)}')

            data = []
            # subset our track data to the chormosome we are dealijng with
            chromosome_track_data = track_data.loc[
                track_data['chr'] == chromosome.replace('chr', '')]

            for track_index, track_row in chromosome_track_data.iterrows():
                cnv_value = track_row['value']
                if cnv_value < -2:
                    cnv_value = -2

                data.append(
                    [track_row['start'], cnv_value])

            # track data series
            plt.add_series(dict(
                symbolSize=2,
                type='scatter',
                itemStyle={'color': util.Colors.grey60},
                xAxisIndex=track_grid_index,
                yAxisIndex=track_grid_index,
                datasetIndex=master_dataset_index
            ))

            # add track dataset
            plt.add_dataset(dict(source=data))

            visual_map.append(dict(
                left='right',
                show=False,
                min=-1,
                max=1,
                seriesIndex=master_dataset_index,
                inRange={
                    'color': [
                        util.Colors.cerulean,
                        util.Colors.grey60,
                        util.Colors.cinnabar]},
                text=['>0', '<0'],
                calculable=False))

            # increment our dataset index
            master_dataset_index += 1
            logger.debug(f'Dataset index : {master_dataset_index}')

        else:
            chromosome_grid_index = count
            logger.debug(f'Chromosome grid index : {chromosome_grid_index}')

        for blocks_data in blocks_list:

            # subset our bands data to the chormosome we are dealing with
            blocks_data_chr = blocks_data.loc[
                blocks_data['chr'] == chromosome]

            blocks_dataset = dict()
            for index_blocks, row_blocks in blocks_data_chr.iterrows():
                if row_blocks['color'] not in blocks_dataset:
                    blocks_dataset[row_blocks['color']] = list()
                blocks_dataset[row_blocks['color']].append([
                    row_blocks['chr'],
                    row_blocks['start'],
                    row_blocks['end'],
                    row_blocks['end']-row_blocks['start']])

            for count, (data_type, data) in enumerate(blocks_dataset.items()):

                if data_type == 0:
                    continue

                plt.add_series(dict(
                    xAxisIndex=len(xaxis),
                    yAxisIndex=len(yaxis),
                    datasetIndex=master_dataset_index,
                    type='custom',
                    itemStyle={'color': data_type},
                    encode={
                        'x': [1, 2],
                        'y': 0},
                    renderItem=MakeRectangles(height=0.7)))

                # add bands dataset
                plt.add_dataset(dict(source=data))

                # increment our dataset index
                master_dataset_index += 1
                logger.debug(f'Dataset index : {master_dataset_index}')

        show = False
        if count+1 == len(sizes):
            show = True

        # axes for chromsome ideogram
        xaxis.append({
            'gridIndex': chromosome_grid_index,
            'show': show,
            'max':  max(sizes['size'])})
        yaxis.append({
            'gridIndex': chromosome_grid_index,
            'axisLine': {'show': False},
            'axisTick': {'show': False},
            'type': 'category',
            'data': [{'value': row['chr']}]})

        # chromsome outlines
        plt.add_series(dict(
            type='custom',
            xAxisIndex=chromosome_grid_index,
            yAxisIndex=chromosome_grid_index,
            itemStyle={
                'color': 'rgba(0, 0, 0, 0)',
                'borderColor': util.Colors.not_black,
                'borderWidth': 3,
                'borderCap': 'round'},
            datasetIndex=master_dataset_index,
            encode={
                'x': [1, 2],
                'y': 0},
            renderItem=MakeRectangles(height=0.7)))

        plt.add_dataset(
            dict(source=[[row['chr'], 0, row['size'], row['size']]]))

        master_dataset_index += 1
        logger.debug(f'Dataset index : {master_dataset_index}')

    plt.grid = grid
    plt.xAxis = xaxis
    plt.yAxis = yaxis
    plt.visualMap = visual_map

    return plt


def main(args):
    """Plot some chromosomes."""
    bands = pd.read_csv(args.bands, sep="\t", header=None)

    bands.name = 'bands'

    copy_number = pd.read_csv(args.blocks, sep="\t", header=None)

    track_data = pd.read_csv(args.tracks, sep="\t", header=None)

    track_data['color'] = util.Color.grey70

    plot = ideoplot(
        blocks=[bands, copy_number],
        track=track_data,
        genome=args.genome)

    plot.render_html(args.output, height="1000px")


def argparser():
    """Argument parser for entrypoint."""
    parser = argparse.ArgumentParser(
        'ezChart ideoplot Demo',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=False
    )
    parser.add_argument(
        "--genome",
        default='hg38',
        help=(
            "Genome build to use",
            "hg19/hg38"
        )
    )
    parser.add_argument(
        "--bands",
        default=resource_filename(
            'ezcharts',
            "plots/data/ideoplots/reference/hg38/cytoBand.txt.gz"),
        help="File to plot as chromosome bands"
    )
    parser.add_argument(
        "--blocks",
        default=resource_filename(
            'ezcharts',
            "plots/data/ideoplots/datasets/hg38/cnv_data.bed.gz"),
        help="File to plot as rectangles on chromosomes"
    )
    parser.add_argument(
        "--tracks",
        default=resource_filename(
            'ezcharts',
            "plots/data/ideoplots/datasets/hg38/cnv_data.bed.gz"),
        help="File to plot as a scatter plot"
    )
    parser.add_argument(
        "--output",
        default="ezchart_ideoplot.html",
        help="Output HTML file."
    )
    return parser
