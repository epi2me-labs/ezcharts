"""Ideoplots."""

import argparse

import pandas as pd
from pkg_resources import resource_filename

from ezcharts.plots import Plot, util


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


def load_ucsc_bands(genome="hg38", types=None):
    """Load "standard" UCSC bands from included BED file.

    :param genome:
    :param types: a list of (stain) types to include.
    """
    # TODO: clean up package data
    src = resource_filename(
        "ezcharts",
        f"data/reference/{genome}/cytoBand.txt.gz")
    if types is None:
        types = [
            'acen', 'gneg',
            'gpos25', 'gpos50', 'gpos75', 'gpos100',
            'gvar', 'stalk']

    names = ['chr', 'start', 'end', 'name', 'type']
    bands_df = pd.read_csv(src, sep="\t", header=None, names=names)
    # annotate with colours, this is why this is isn't a generic
    # function - we assume a set of types.
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
    bands_df = bands_df[bands_df['type'].isin(types)]
    return bands_df


def load_chr_sizes(genome="hg38"):
    """Load chr size data.

    :param genome:
    """
    # TODO: clean up package data
    src = resource_filename(
        "ezcharts",
        f"data/reference/{genome}/{genome}.chrom.sizes.gz")
    sizes = pd.read_csv(src, sep="\t", header=None, names=['chr', 'size'])
    sizes['chr'] = sizes['chr'].str.replace('chr', '')
    return sizes


def ideogram(blocks=None, track=None, genome='hg38'):
    """Draw an ideogram in various styles.

    :param blocks:
    :param track:
    """
    # TODO: a legend?

    if blocks is not None and not isinstance(blocks, (list, tuple)):
        blocks = [blocks]

    blocks_list = list()

    # find known 'blocks' datasets, actually these are currently all
    # just subsets of the bands dataset loaded as a single thing
    # and coloured by the band name.
    named_dsets = [x for x in blocks if isinstance(x, str)]
    if 'cytobands' in named_dsets:
        named_dsets = None
    if named_dsets is None or len(named_dsets):
        blocks_list.append(
            load_ucsc_bands(genome, named_dsets))

    # other blocks items given as dataframe with some required fields
    for user_dset in (x for x in blocks if isinstance(x, pd.DataFrame)):
        req_fields = pd.Series(['chr', 'start', 'end', 'color'])
        if req_fields.isin(user_dset.columns).all():
            dset = user_dset.copy()
            dset['chr'] = dset['chr'].str.replace('chr', '')
            blocks_list.append(dset)
        else:
            raise TypeError(
                "Provided blocks dataframe does not contain required fields: "
                f"{req_fields.tolist()}. Found {user_dset.columns.tolist()}")

    if track is not None:
        # note, no colour -- this is hardcoded in visual map
        # TODO: don't do this
        req_fields = pd.Series(['chr', 'start', 'value'])
        if req_fields.isin(track.columns).all():
            track_data = track.copy()
            track_data['chr'] = track_data['chr'].str.replace('chr', '')
        else:
            raise TypeError(
                "Provided trakcs dataframe does not contain required fields: "
                f"{req_fields.tolist()}")

    # need chrom sizes for outer boxes
    sizes = load_chr_sizes(genome)

    # off we go
    plt = Plot()

    # setup some variables that define our grid
    if track is None:
        top_increment, height = 4, 4
    else:
        top_increment, height = 2.0, 1.7

    grid = list()
    xaxis = list()
    yaxis = list()
    visual_map = list()
    chr_sizes = list()
    top = 1

    # this keeps count of total datasets added
    master_dataset_index = 0
    for count, (index, row) in enumerate(sizes.iterrows()):
        chromosome, chrom_size = row['chr'], row['size']
        # only consider main assembly
        if "_" in row['chr']:
            continue

        chr_sizes.append({
            'value': [chromosome, 0, chrom_size, chrom_size],
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

        if track is not None:
            grid.append({
                'left': '3.5%',
                'top': f'{top}%',
                'width': '90%',
                'height': f'{height}%'})

            top += top_increment + 0.05

            # These are the grid and x/yaxis index for tracks - i.e odd
            track_grid_index = 2 * count if count != 0 else 0

            # This is the grid index and x/yaxis for chromosomes - i.e. even
            chromosome_grid_index = (2 * count) + 1 if count != 0 else 1

            # track axes
            xaxis.append({
                'gridIndex': track_grid_index,
                'show': False,
                'max': max(sizes['size'])})

            yaxis.append({
                'gridIndex': track_grid_index,
                'min': -2.2,
                'max': 2.2,
                'type': 'value',
                'position': 'right',
                'interval': 2.2,
                'axisLine': {'onZero': False}})

            # subset our track data to the chromosome we are dealing with
            data = track_data.loc[
                track_data['chr'] == chromosome]
            data = data[['start', 'value']].values.tolist()

            # track data series
            plt.add_series(dict(
                symbolSize=2,
                type='scatter',
                itemStyle={'color': util.Colors.grey60},
                xAxisIndex=track_grid_index,
                yAxisIndex=track_grid_index,
                datasetIndex=master_dataset_index))
            plt.add_dataset(dict(source=data))

            # TODO: ONE FOR LATER, this is not generic
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
        else:  # adding track
            chromosome_grid_index = count

        # now add blocks
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
                plt.add_dataset(dict(source=data))

                # increment our dataset index
                master_dataset_index += 1

        # showing something?
        show = False
        if count + 1 == len(sizes):
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

        # chromosome outlines
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

    plt.grid = grid
    plt.xAxis = xaxis
    plt.yAxis = yaxis
    plt.visualMap = visual_map
    return plt


def main(args):
    """Plot some chromosomes."""
    blocks = list()
    if args.show_bands:
        blocks.append('cytobands')
    if args.blocks is not None:
        blk = pd.read_csv(
            args.blocks, sep="\t", header=None,
            names=['chr', 'start', 'end'])
        blk['color'] = util.Colors.grey70
        blocks.append(blk)
    track_data = None
    if args.track is not None:
        track_data = pd.read_csv(
            args.track, sep="\t", header=None,
            names=['chr', 'start', 'end', 'value'])
        track_data['value'] = track_data['value'].clip(lower=args.track_floor)

    plot = ideogram(blocks=blocks, track=track_data, genome=args.genome)
    plot.render_html(args.output, height="1000px")


def argparser():
    """Argument parser for entrypoint."""
    parser = argparse.ArgumentParser(
        'ezChart ideogram Demo',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=False)
    parser.add_argument(
        "--genome",
        default='hg38',
        choices=["hg38", "hg19"],
        help="Genome build to use")
    parser.add_argument("--show_bands", action='store_true')
    parser.add_argument(
        "--blocks",
        default=None,
        help="File to plot as rectangles on chromosomes")
    parser.add_argument(
        "--track",
        default=None,
        help="File to plot as a scatter plot")
    parser.add_argument(
        "--output",
        default="ezchart_ideogram.html",
        help="Output HTML file.")
    return parser
