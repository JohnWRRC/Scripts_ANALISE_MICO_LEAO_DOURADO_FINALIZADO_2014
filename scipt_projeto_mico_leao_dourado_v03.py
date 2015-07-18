import grass.script as grass
from grass.script import raster as grassR
import os
import string
import glob
import re
import fnmatch
LISTA=['B06','B07','C06','C07','D04','D05','D06','D07','D08','E04','E05','E06','E07','E08','F04','F05','F06','F07','F08','G05','G06','G07','G08','H04','H05','H06','H07','H08','IO4','I05','I06','I07','I08','J04','J06','J07']
caminho_pasta_shp='r"F:\data\john_pc2\micro_leao\shps\\'''
NM_shp_amostras='amostras_teste_v03.shp'
InAmostras=caminho_pasta_shp+NM_shp_amostras


grass.run_command('v.in.ogr', dsn=InAmostras, out='amostras_shp', flags='o', verbose=False,overwrite=True)



for i in LISTA:
    query="grade=\'"+i+"\'" ## criando variavel de nome de coluna
    x=grass.read_command('v.db.select', flags='c', map='area_classificacao_2012_grid0125b_v02_shp', column='NM_image', where=query,verbose=False) ##extraindo o/os nome(s) da(s) imagem(s)
    grass.run_command('v.extract', input='area_classificacao_2012_grid0125b_v02_shp', output='temp', where=query, type='area', new=1,overwrite=True,verbose=False) ##extraindo o quadrante do shp
    grass.run_command('v.to.rast', input='temp', out='temp_rast_masc', use="cat",overwrite=True,verbose=False) ##rasterizando o quadrante que sera usado como MASK 
  
    
    print x 
    #imprimindo o nome extraido da coluna NM_image do shp area_classificacao_2012_grid0125b_v02_shp
    a=re.split(',',x) ## criando uma variavel de ambiente dizendo que não eh uma lista mas tem que estar separado por virgula se houver mais de um 
    
    
    cont=0 ## variavel de controle
    print a 
    letras=['A','B','C'] ## letras para atribui caso aja mais de uma imegens dentro da mesma quadricula
    for k in a:
        k=str(k).replace("\n","") ##criando a variavel k ,tratamento na variavel "a" retirando o  "\n"
        print k
        lista_arquivos=[] ## criando lista vazia para armazenar as imagens encontradas, caso aja mais de uma com o mesmo nome
        for root, dirs, files in os.walk("F:/data/john_pc2/micro_leao/Rapdeye/2012/Articulacao/Silva Jardim/provision-26962"):
            for file in files:
                if file.endswith(k): ## o "k" contem os nomes das imagens  encontradas, podendo ser apensa uma 
                    print os.path.join(root, file)
                    lista_arquivos.append(os.path.join(root, file)) ## atribuindo o print com o caminho seguido do nome da imagem a lista_arquivos
        if (len(lista_arquivos)>1):
            print "MENSAGEM FORAM ENCONTRADOS :",lista_arquivos, "UTILIZANDO O PRIMEIRO" ##mensagem para avisar o usuario que foram enoontrados mais de um arquivo com o mesmo nome.
            
        j=i ## criando variavel j para controlar a atribuição das lestras
        if len(a)>1:
            j=i+"_"+letras[cont] ## se a nossa lista hover mais de uma string, "j" passa ser o "i" + um item da lista de LETRAS, controlado pelo cont
            cont=cont+1 ## incrementando o contador
        print j
        print lista_arquivos
        grass.run_command ('r.in.gdal', flags='o' ,input=lista_arquivos[0], output=j ,overwrite=True, verbose = False) ##importando a imagem armazenada na lista_arquivos sempre [0]
        grass.run_command('g.region', rast=j+'.1',verbose=False) ## g.region da imagem para raterização das amostras, isso foi feito para utilzar a extensão
        grass.run_command('v.to.rast', input='amostras_shp', out='amostras_raster', use='attr', column='cod', overwrite=True,verbose=False) ## rasterizando as amostras
        grass.run_command('r.reclass', input='amostras_raster', out='amostras_raster_reclass', rules='F:/data/john_pc2/micro_leao/regra_reclass.txt',overwrite=True,verbose=False) ##reclassificndo as amostras
        grass.run_command('r.mask', input='temp_rast_masc', flags='o', verbose=False ) ##criando mascara com o quadrante extraido para aliviar o processamento
        grass.run_command('i.group', group=j ,subgroup=j,  input=j+'.1' ',' +j+'.2' ',' +j+'.3',verbose=False) ## criando grupo com as bandas
        grass.run_command('i.gensigset', trainingmap='amostras_raster_reclass', group=j, subgroup=j, signaturefile=j+'_sigfile_to_smap',overwrite=True,verbose=False) ## craindo assinatura 
        grass.run_command('g.region', rast=j+'.1',verbose=False) ## reforçando a janela de trabalho
        grass.run_command('i.smap', group=j, subgroup=j, signaturefile=j+'_sigfile_to_smap', output=j+'_classificacao_smap', blocksize=2048,verbose=False) ##classificando a imagem
        grass.run_command('r.neighbors', input=j+'_classificacao_smap', out=j+'_classificacao_smap_limpo_05', method='mode', size=05,verbose=False) ##limpando a imagem 
        grass.run_command('r.to.vect', input=j+'_classificacao_smap_limpo_05', out=j+'_classificacao_smap_limpo_05_vect', feature='area',verbose=False ) ## vetorizando a calssificação 
        grass.run_command('r.out.gdal', input=j+'_classificacao_smap_limpo_05', out=j+'_classificacao_smap_limpo_05_tif.tif', format='GTiff',verbose=False)## exportando o raster da calssificação
        grass.run_command('v.out.ogr', input=j+'_classificacao_smap_limpo_05_vect', dsn=j+'_classificacao_smap_limpo_05_vect.shp', type='area',verbose=False)## exportando o vetor da classifcção
        grass.run_command('r.mask', flags='r',verbose=False) ## removendo mascara
        grass.run_command('g.remove',flags='f', vect='temp',verbose=False) ##removendo arquuivo temporario
        grass.run_command('g.remove',flags='f', rast='temp_rast_masc',verbose=False) ##removendo arquuivo temporario
        grass.run_command('g.remove',flags='f', rast='amostras_raster_reclass',verbose=False) ##removendo arquuivo temporario
        grass.run_command('g.remove',flags='f', rast='amostras_raster',verbose=False) ##removendo arquuivo temporario
        
      