import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter, FormatStrFormatter, FuncFormatter, NullFormatter

def f_fmt_func(x, pos):
    if pos % 3 == 0:
        return '%1.1fM' % (x*1e-6)
    return ''

f_fmt = FuncFormatter(f_fmt_func)
x_fmt = FormatStrFormatter('%.0f')
fig_extension = "png"

# the first line is title
def toTable(input, theme = "display"):
    for i in range(len(input)):
        if (len(input[i]) != len(input[0])):
            print("ERROR! Invalid format in row {}!".format(i))
            print(input[0])
            print(input[i])
            return ""

    in_line = ""
    enter = ""
    first = ""
    middle = ""
    last = ""
    if theme == "csv":
        in_line = ","
        first = ""
        middle = "\n"
        enter = "\n"
        last = ""
    elif theme == "complex":
        in_line = "&"
        enter = "^_^\n"
        first =  "=======================================\n"
        middle = "\n---------------------------------------\n"
        last =   "***************************************\n"
    elif theme == 'display':
        in_line = '\t'
        first = ""
        middle = "\n"
        enter = "\n"
        last = ""
    elif theme == 'latex':
        first = ''
        in_line = ' & '
        middle = '\n'
        enter = ' \\\\ \\hline\n'
        last = ''
    else:
        print("ERROR! Theme {} not support!".format(theme))
        return ""
    # TODO latex theme

    # and more format ...
    st = first
    is_title = True
    for item in input:
        is_first = True
        for x in item:
            if (not is_first):
                st += in_line
            is_first = False
            st += str(x)
        if (is_title):
            st += middle
            is_title = False
        else:
            st += enter
    st += last
    return st

class WeakDataFormat:
    def __init__(self):
        self.Av = []
        self.Mv = []
        self.nodes = []
        self.label = []

    def add(self, model):
        self.Av.append(model['json-log']['Av_time'])
        self.Mv.append(model['json-log']['Mv_time'])
        self.nodes.append(model['nodes'])
        self.label.append(model['label'])

    def calc_eff(self):
        self.Av_eff = [self.Av[0] / t for t in self.Av]
        self.Mv_eff = [self.Mv[0] / t for t in self.Mv]

def plot_weak(done):
    # table
    tb_detail = [['model', 'nn', 'np', 'ele', 'Ag', 't_Av', 't_Mv']]
    for model in done:
        log = model['json-log']
        tb_detail.append([log['model'],
                         log['nn'],
                         log['np'],
                         log['elements'],
                         log['Ag_size'],
                         log['Av_time'],
                         log['Mv_time']])
    f = open('plot/weak.table', "w")
    f.write(toTable(tb_detail, 'latex'))
    f.close()

    plt.figure(figsize = [12, 5])
    # plot time
    ax = plt.subplot(1, 2, 1)
    groups = [WeakDataFormat(), WeakDataFormat()]
    for model in done:
        groups[model['group']].add(model)
    for i in range(2):
        plt.plot(groups[i].nodes, groups[i].Av, '-', label="Av (M1-3)", linewidth=0.7, marker='x', markersize=8)
        plt.plot(groups[i].nodes, groups[i].Mv, '-', label="Mv (M4-6)", linewidth=0.7, marker='.', markerfacecolor='none', markersize=8)
    plt.xscale('log')
    plt.xlabel("number of nodes")
    plt.ylabel("time (s)")
    plt.grid(True, which='both')
    ax.xaxis.set_minor_formatter(x_fmt)
    ax.xaxis.set_major_formatter(x_fmt)
    plt.legend(loc='upper left')

    # plot efficiency, assume done[0] is test M1
    ax = plt.subplot(1, 2, 2)
    for i in range(2):
        groups[i].calc_eff()
        plt.plot(groups[i].nodes, groups[i].Av_eff, '-', label="Av (M1-3)", linewidth=0.7, marker='x', markersize=8)
        plt.plot(groups[i].nodes, groups[i].Mv_eff, '-', label="Mv (M4-6)", linewidth=0.7, marker='.', markerfacecolor='none', markersize=8)
    plt.xscale('log')
    plt.xlabel("number of nodes")
    plt.ylabel("efficiency")
    ax.xaxis.set_minor_formatter(x_fmt)
    ax.xaxis.set_major_formatter(x_fmt)
    plt.grid(True, which='both')
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.savefig("plot/weak.{}".format(fig_extension))
    # plt.show()  # we can add this line while not on cluster
    plt.close()

def plot_fix(done):
    # table
    tb_detail = [['model', '(ln, lx)', '(xi,eta)',  '(deg, #it)', '#eigs', 'total']]
    for model in done:
        log = model['json-log']
        tb_detail.append([log['model'],
                         "({},{})".format(log['lambda_min'], log['lambda_max']),
                         "({},{})".format(log['xi'], log['eta']),
                         "({},{})".format(log['deg'], log['it']),
                         log['num_eigs'],
                         log['tot_time']])

    f = open('plot/fix.table', "w")
    f.write(toTable(tb_detail, 'latex'))
    f.close()

    # plot
    tb_plot = [['model', 'size', 'deg', 'it', 'time']]
    size = []
    deg = []
    it = []
    tm = []
    for model in done:
        log = model['json-log']
        tb_plot.append([
            log['model'],
            log['Ag_size'],
            log['deg'],
            log['it'],
            log['tot_time']
        ])
        size.append(log['Ag_size'])
        deg.append(log['deg'])
        it.append(log['it'])
        tm.append(log['tot_time'])
    
    # not sure how to plot
    plt.figure(figsize = [15, 5])

    ax = plt.subplot(1,3,1)
    plt.plot(size, deg, 'r-', linewidth=0.7, marker='x', markersize=8)
    plt.xticks(size)
    plt.xscale('log')
    plt.xlabel('size')
    plt.ylabel('degree')
    plt.grid(True, which='both')
    ax.xaxis.set_major_formatter(NullFormatter())
    ax.xaxis.set_minor_formatter(f_fmt)

    ax = plt.subplot(1,3,2)
    plt.plot(size, it, 'g-', linewidth=0.7, marker='.', markerfacecolor='none', markersize=8)
    plt.xticks(size)
    plt.xscale('log')
    plt.xlabel('size')
    plt.ylabel('iterations')
    plt.grid(True, which='both')
    ax.xaxis.set_major_formatter(NullFormatter())
    ax.xaxis.set_minor_formatter(f_fmt)

    ax = plt.subplot(1,3,3)
    plt.plot(size, tm, 'b-', linewidth=0.7, marker='+', markersize=8)
    plt.xticks(size)
    plt.xscale('log')
    plt.xlabel('size')
    plt.ylabel('total time (s)')
    plt.grid(True, which='both')
    ax.xaxis.set_major_formatter(NullFormatter())
    ax.xaxis.set_minor_formatter(f_fmt)

    plt.subplots_adjust(wspace=0.3, hspace=0)
    plt.tight_layout()
    plt.savefig("plot/fix.{}".format(fig_extension))
    # plt.show()   # we can add this line while not on cluster
    plt.close()
    
def plot_strong(done):
    C3_nn = [4, 8, 16, 32]
    C3_np = [192, 384, 768, 1536]
    C3_tm = [6854.54, 3247.78, 1779.14, 1259.08]
    C3_eff = [1.0, 1.1, 0.96, 0.68]
    E3_nn = [4, 8, 16]
    E3_np = [192, 384, 768]
    E3_tm = [34319.28, 16570.22, 10071.56]
    E3_eff = [1.0, 1.0, 0.85]
    M3_nn = []
    M3_np = []
    M3_tm = []
    M3_eff = []
    # assume done[0] is the first exp
    tb_detail  = [['nn/np', 'T-Av (s)', 'T-Mv (s)', 'T-M^{-1}v (s)', 'total (s)', 'eff.']]
    div = None
    for model in done:
        log = model["json-log"]
        if div is None:
            div = log['tot_time'] * log['nn'] # NOTE np should be the total thread?
        eff = div / (log['tot_time'] * log['nn'])
        tb_detail.append([
            "{}/{}".format(log['nn'], log['nn']),
            log['Av_time'],
            log['Mv_time'],
            log['rev_M_v_time'],
            log['tot_time'],
            eff
        ])
        M3_nn.append(log['nn'])
        M3_np.append(log['np'])
        M3_tm.append(log['tot_time'])
        M3_eff.append(eff)

    f = open("plot/strong.table", "w")
    f.write(toTable(tb_detail))
    f.close()

    plt.figure(figsize = [8, 5])

    plt.subplot(2, 2, 1)
    plt.plot(C3_nn, C3_tm, "-o", label = "C3 (SKX)")
    plt.plot(E3_nn, E3_tm, "-*", label = "E3 (SKX)")
    plt.ylabel("time (s)")
    plt.legend()

    plt.subplot(2, 2, 2)
    plt.plot(C3_nn, C3_eff, "-o", label = "C3 (SKX)")
    plt.plot(E3_nn, E3_eff, "-*", label = "E3 (SKX)")
    plt.ylabel("efficiency")
    plt.legend()

    plt.subplot(2, 2, 3)
    plt.plot(M3_nn, M3_tm, "-o", label = "M3 (???)")
    plt.ylabel("time (s)")
    plt.legend()

    plt.subplot(2, 2, 4)
    plt.plot(M3_nn, M3_eff, "-*", label = "M3 (???)")
    plt.ylabel("efficiency")
    plt.legend()

    plt.savefig("plot/strong.{}".format(fig_extension))
    plt.show()
    plt.close()


