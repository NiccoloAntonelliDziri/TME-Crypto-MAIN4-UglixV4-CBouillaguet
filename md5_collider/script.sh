#!/bin/bash

# Changez username
username="niccolo"
username_length=${#username}
padding_length=$((64 - username_length))

# Création du préfixe avec la taille appropriée (64 octets)
padding=$(printf '0%.0s' $(seq 1 ${padding_length}))
prefix="${username}${padding}"

# Création du fichier de préfixe
echo -n "${prefix}" > prefix_file

# Initialisation de la variable de contrôle
md5_equal=false

while [ "$md5_equal" = false ]; do
  # Recherche de la première collision
  ./coll_finder prefix_file A B

  # Concaténation des préfixes et des collisions
  cat prefix_file A > prefix_A
  cat prefix_file B > prefix_B

  # Recherche de la deuxième collision
  ./coll_finder prefix_A C D

  # Concaténation des préfixes et des collisions
  cat prefix_A C > prefix_AC
  cat prefix_A D > prefix_AD
  cat prefix_B C > prefix_BC
  cat prefix_B D > prefix_BD

  #Ajout "h4ckm0d3"
  sed -i 's/$/h4ckm0d3/' prefix_AC
  sed -i 's/$/h4ckm0d3/' prefix_AD
  sed -i 's/$/h4ckm0d3/' prefix_BC
  sed -i 's/$/h4ckm0d3/' prefix_BD

  # Vérification des empreintes MD5, SINON on recommence
  md5_1=$(md5sum prefix_AC | awk '{ print $1 }')
  md5_2=$(md5sum prefix_AD | awk '{ print $1 }')
  md5_3=$(md5sum prefix_BC | awk '{ print $1 }')
  md5_4=$(md5sum prefix_BD | awk '{ print $1 }')

  if [ "$md5_1" = "$md5_2" ] && [ "$md5_1" = "$md5_3" ] && [ "$md5_1" = "$md5_4" ]; then
    md5_equal=true
  fi
done

echo "Empreintes MD5 égales : $md5_1"

# Conversion des fichiers en hexadécimal
xxd -p prefix_AC > 0
xxd -p prefix_AD > 1
xxd -p prefix_BC > 2
xxd -p prefix_BD > 3

# On supprime les sauts de ligne, je vous évite de le faire :)
sed -i ':a;N;$!ba;s/\n//g' 0
sed -i ':a;N;$!ba;s/\n//g' 1
sed -i ':a;N;$!ba;s/\n//g' 2
sed -i ':a;N;$!ba;s/\n//g' 3

