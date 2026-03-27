from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import matplotlib.pyplot as plt
import io, base64

app = Flask(__name__)

# --- Dados iniciais ---
df = pd.DataFrame([
    {'Jogador':'Donuts_mamaco','Golos':887,'Assistências':170,'Wins':307,
     '1v1':675,'2v2':473,'3v3':410,'Torneios':484,'Casual':649,'Data':'27/03/2026'},
    {'Jogador':'Donuts_exe','Golos':149,'Assistências':18,'Wins':46,
     '1v1':478,'2v2':440,'3v3':483,'Torneios':0,'Casual':929,'Data':'27/03/2026'},
    {'Jogador':'Portman12_Games','Golos':202,'Assistências':40,'Wins':59,
     '1v1':264,'2v2':140,'3v3':469,'Torneios':0,'Casual':569,'Data':'27/03/2026'},
    {'Jogador':'Parreirinha8','Golos':206,'Assistências':97,'Wins':99,
     '1v1':381,'2v2':268,'3v3':473,'Torneios':404,'Casual':511,'Data':'27/03/2026'}
])

ADMIN_PASSWORD = "Donuts"

# --- Funções para gerar gráficos ---
def plot_ranks_line(df):
    import matplotlib
    matplotlib.use('Agg')
    ranks_cols = ['1v1','2v2','3v3','Torneios','Casual']
    jogadores = df['Jogador'].unique()
    fig, axes = plt.subplots(1, len(ranks_cols), figsize=(20,5))
    
    for ax, col in zip(axes, ranks_cols):
        for jogador in jogadores:
            sub = df[df['Jogador']==jogador]
            ax.plot(range(len(sub)), sub[col], marker='o', label=jogador)
        ax.set_title(col)
        ax.grid(True)
        ax.set_xticks([])  # remove texto eixo x
    axes[-1].legend(loc='upper left', bbox_to_anchor=(1,1))
    
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close(fig)
    return img

def plot_stats_donut(df):
    import matplotlib
    matplotlib.use('Agg')
    donuts = {}
    for jogador in df['Jogador'].unique():
        sub = df[df['Jogador']==jogador].iloc[-1]
        labels = ['Golos','Assistências','Wins']
        sizes = [sub['Golos'], sub['Assistências'], sub['Wins']]
        fig, ax = plt.subplots(figsize=(4,4))
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax.set_title(jogador)
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        donuts[jogador] = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close(fig)
    return donuts

# --- Rotas ---
@app.route("/", methods=['GET','POST'])
def login():
    if request.method=='POST':
        password = request.form.get('password')
        if password==ADMIN_PASSWORD:
            return redirect(url_for('admin_view'))
        else:
            return redirect(url_for('view_stats'))
    return render_template("login.html")

@app.route("/view")
def view_stats():
    img_ranks = plot_ranks_line(df)
    img_donuts = plot_stats_donut(df)
    return render_template("stats.html", df=df, admin=False, img_ranks=img_ranks, img_donuts=img_donuts)

@app.route("/admin", methods=['GET','POST'])
def admin_view():
    message = ""
    if request.method=='POST':
        jogador = request.form.get('jogador')
        data = request.form.get('data')
        golos = int(request.form.get('golos',0))
        assists = int(request.form.get('assists',0))
        wins = int(request.form.get('wins',0))
        rank_1v1 = int(request.form.get('1v1',0))
        rank_2v2 = int(request.form.get('2v2',0))
        rank_3v3 = int(request.form.get('3v3',0))
        torneios = int(request.form.get('torneios',0))
        casual = int(request.form.get('casual',0))
        
        new_row = {'Jogador':jogador,'Golos':golos,'Assistências':assists,'Wins':wins,
                   '1v1':rank_1v1,'2v2':rank_2v2,'3v3':rank_3v3,'Torneios':torneios,
                   'Casual':casual,'Data':data}
        global df
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        message = "Estatísticas adicionadas!"
    
    img_ranks = plot_ranks_line(df)
    img_donuts = plot_stats_donut(df)
    jogadores = df['Jogador'].unique()
    return render_template("stats.html", df=df, admin=True, img_ranks=img_ranks, img_donuts=img_donuts, jogadores=jogadores, message=message)

if __name__=="__main__":
    app.run(debug=True)